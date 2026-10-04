#!/usr/bin/env python3
"""
Genera gli screenshot delle pagine del pannello M-1.

Non sono mockup: usa gli stessi font della configurazione, disegna su una
griglia 64x64, applica la stessa soglia a 1 bit del pannello e poi rende i
LED come punti. Quello che si vede e' quello che il pannello mostra.

Uso:  python3 tools/screenshots.py [cartella_output]
Serve: pillow, piu' Silkscreen-Regular.ttf e materialdesignicons-webfont.ttf
       nella cartella indicata da FONT_DIR.
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.environ.get("FONT_DIR", "/home/claude/fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/img"
W = H = 64
SCALE = 8

SILK = os.path.join(FONT_DIR, "Silkscreen-Regular.ttf")
MDI = os.path.join(FONT_DIR, "mdi.ttf")

f_xs = ImageFont.truetype(SILK, 8)
f_md = ImageFont.truetype(SILK, 16)
f_lg = ImageFont.truetype(SILK, 18)
f_ic14 = ImageFont.truetype(MDI, 14)
f_ic28 = ImageFont.truetype(MDI, 28)

# codepoint come nelle substitution della configurazione
MDI_NIGHT = "\U000F0594"
MDI_UMBRELLA = "\U000F054A"
MDI_MOWER = "\U000F11F7"
MDI_AIR = "\U000F0D43"
MDI_WASHING = "\U000F072A"

DIM = (140, 140, 150)
WHITE = (255, 255, 255)
GREEN = (0, 230, 90)
AMBER = (255, 170, 30)
RED = (255, 60, 50)
BLUE = (70, 150, 255)
CYAN = (90, 200, 255)
SOLAR = (255, 190, 40)


class Panel:
    """Le primitive hanno gli stessi nomi dei lambda ESPHome."""

    def __init__(self):
        self.img = Image.new("RGB", (W, H), (0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def _mask(self, text, font):
        bb = font.getbbox(text)
        m = Image.new("L", (max(1, bb[2] - bb[0] + 2), max(1, bb[3] + 2)), 0)
        ImageDraw.Draw(m).text((-bb[0], 0), text, font=font, fill=255)
        return m.point(lambda v: 255 if v > 110 else 0), bb

    def print(self, x, y, font, color, text, align="left"):
        mask, bb = self._mask(text, font)
        xx = x - mask.width // 2 if align == "center" else x
        # la maschera conserva gia' l'offset verticale del glifo: y e' il bordo
        # alto della riga, come TOP_LEFT in ESPHome
        self.img.paste(Image.new("RGB", mask.size, color), (int(xx), int(y)), mask)

    def rectangle(self, x, y, w, h, color):
        self.d.rectangle([x, y, x + w - 1, y + h - 1], outline=color)

    def filled_rectangle(self, x, y, w, h, color):
        if w > 0 and h > 0:
            self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

    def text_w(self, text, font):
        bb = font.getbbox(text)
        return bb[2] - bb[0]

    def cornici(self, allarme=None, rifiuti=None):
        """rifiuti: 'carta' | 'plastica' | 'secco' ; allarme: 'armed' | 'arming'"""
        col = {"carta": (255, 200, 0), "plastica": (40, 120, 255), "secco": (170, 70, 220)}
        if rifiuti:
            self.rectangle(1, 1, 62, 62, col[rifiuti])
            self.rectangle(2, 2, 60, 60, col[rifiuti])
        if allarme == "armed":
            self.rectangle(0, 0, 64, 64, (150, 20, 20))
        elif allarme == "arming":
            self.rectangle(0, 0, 64, 64, (190, 120, 0))

    def save(self, name):
        out = Image.new("RGB", (W * SCALE, H * SCALE), (7, 7, 10))
        dd = ImageDraw.Draw(out)
        r = SCALE * 0.38
        px = self.img.load()
        for y in range(H):
            for x in range(W):
                c = px[x, y]
                acceso = max(c) > 20
                cx, cy = x * SCALE + SCALE / 2, y * SCALE + SCALE / 2
                dd.ellipse([cx - r, cy - r, cx + r, cy + r],
                           fill=c if acceso else (19, 19, 24))
        path = os.path.join(OUT, name)
        out.save(path)
        print("  ", path)


def hhmm_bar(p, frac, x, y, w, h, color):
    p.rectangle(x, y, w, h, (90, 90, 100))
    fh = int(frac * (h - 2))
    if fh > 0:
        p.filled_rectangle(x + 1, y + h - 1 - fh, w - 2, fh, color)


# --------------------------------------------------------------- pagine ----
def home(ora="21:57", giorno=4, mese="OTT", temp=14, **k):
    p = Panel()
    p.cornici(**k)
    font = f_lg if p.text_w("88:88", f_lg) <= 62 else f_md
    p.print(32, 2, font, WHITE, ora, "center")
    p.print(32, 31, f_xs, (105, 105, 112), f"{giorno} {mese}", "center")
    p.print(16, 44, f_ic14, (190, 190, 200), MDI_NIGHT, "center")
    buf = f"{temp:.0f}"
    bw = p.text_w(buf, f_md)
    x0 = 44 - (bw + 5) // 2
    p.print(x0, 42, f_md, WHITE, buf)
    p.filled_rectangle(x0 + bw + 2, 46, 3, 3, WHITE)
    return p


def energia(pv=3200, grid=-1850, bsoc=86, bpw=2100, **k):
    p = Panel()
    p.cornici(**k)
    cg = GREEN if grid < -100 else RED if grid > 100 else AMBER
    cb = GREEN if bpw > 50 else AMBER if bpw < -50 else DIM
    p.print(2, 0, f_xs, DIM, "SOLARE")
    p.print(2, 9, f_xs, SOLAR, f"{pv/1000:.1f} kW")
    p.print(2, 21, f_xs, DIM, "RETE")
    p.print(2, 30, f_xs, cg, f"{grid:+.0f} W")
    p.print(2, 42, f_xs, DIM, f"BATT {bsoc:.0f}%")
    p.print(2, 51, f_xs, cb, f"{bpw/1000:+.1f} kW")
    hhmm_bar(p, min(1, pv / 6000), 50, 6, 12, 54, SOLAR)
    return p


def auto(soc=62, kw=7.4, **k):
    p = Panel()
    p.cornici(**k)
    x0, y0, w, h = 6, 8, 48, 16
    p.rectangle(x0, y0, w, h, (200, 200, 200))
    p.filled_rectangle(x0 + w, y0 + 5, 3, 6, (200, 200, 200))
    bc = RED if soc < 20 else AMBER if soc < 60 else GREEN
    p.filled_rectangle(x0 + 2, y0 + 2, int(soc / 100 * (w - 4)), h - 4, bc)
    p.print(32, 28, f_md, WHITE, f"{soc:.0f}%", "center")
    p.print(32, 50, f_xs, CYAN, f"{kw:.1f} kW", "center")
    return p


def pioggia_ora(mm24=12.4, **k):
    p = Panel()
    p.cornici(**k)
    p.print(32, 2, f_ic28, BLUE, MDI_UMBRELLA, "center")
    p.print(32, 32, f_md, BLUE, "PIOVE", "center")
    p.print(32, 52, f_xs, (120, 150, 200), f"{mm24:.1f} MM 24H", "center")
    return p


def pioggia_prev(minuti=25, **k):
    p = Panel()
    p.cornici(**k)
    p.print(32, 2, f_ic28, BLUE, MDI_UMBRELLA, "center")
    p.print(32, 32, f_md, BLUE, f"{minuti:.0f} MIN", "center")
    p.print(32, 52, f_xs, (120, 150, 200), "PIOGGIA", "center")
    return p


def rasaerba(errore=False, **k):
    p = Panel()
    p.cornici(**k)
    c = RED if errore else (0, 220, 120)
    p.print(32, 4, f_ic28, c, MDI_MOWER, "center")
    p.print(32, 42, f_xs, c, "ERRORE" if errore else "IN TAGLIO", "center")
    return p


def aria(v=32, **k):
    p = Panel()
    p.cornici(**k)
    c = GREEN if v < 15 else AMBER if v < 25 else RED
    p.print(32, 0, f_ic14, c, MDI_AIR, "center")
    p.print(32, 15, f_xs, (150, 150, 160), "PM2.5", "center")
    p.print(32, 26, f_md, c, f"{v:.0f}", "center")
    p.print(32, 44, f_xs, (110, 110, 120), "ug/m3", "center")
    p.rectangle(4, 56, 56, 6, (90, 90, 100))
    p.filled_rectangle(4, 56, min(56, int(v / 50 * 56)), 6, c)
    return p


def allarme():
    p = Panel()
    c = (255, 30, 20)
    p.filled_rectangle(0, 0, 64, 12, c)
    p.filled_rectangle(0, 52, 64, 12, c)
    p.print(32, 22, f_xs, WHITE, "ALLARME", "center")
    p.print(32, 36, f_xs, c, "INTRUSIONE", "center")
    return p


def alert(**k):
    p = Panel()
    p.cornici(**k)
    c = (0, 200, 255)
    p.print(32, 2, f_ic28, c, MDI_WASHING, "center")
    p.print(32, 32, f_xs, c, "LAVATRICE", "center")
    p.print(32, 46, f_xs, (220, 220, 220), "finita", "center")
    return p


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("Genero gli screenshot in", OUT)
    home().save("page-home.png")
    energia().save("page-energia.png")
    auto().save("page-auto.png")
    pioggia_ora().save("page-pioggia-ora.png")
    pioggia_prev().save("page-pioggia-previsione.png")
    rasaerba().save("page-rasaerba.png")
    rasaerba(errore=True).save("page-rasaerba-errore.png")
    aria().save("page-aria.png")
    allarme().save("page-allarme.png")
    alert().save("page-alert.png")
    home(rifiuti="carta").save("cornice-rifiuti-carta.png")
    energia(rifiuti="plastica").save("cornice-rifiuti-plastica.png")
    home(allarme="armed").save("cornice-allarme.png")
    home(allarme="armed", rifiuti="secco").save("cornice-doppia.png")
