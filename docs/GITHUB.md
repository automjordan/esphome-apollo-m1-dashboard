# Pubblicare il repository su GitHub

## 1. Crea il repository vuoto

Su github.com → **New repository**:

- Nome suggerito: `esphome-apollo-m1-dashboard`
- Descrizione: *Display informativo Home Assistant su Apollo M-1 (HUB75 64x64, ESPHome)*
- **Pubblico**
- **Non** spuntare "Add a README", "Add .gitignore" o "Choose a license": li hai gia' e creerebbero un conflitto al primo push.

## 2. Prima di committare: controlla i segreti

Il file `m1-matrix.yaml` usa `!secret`, quindi non contiene password. Verifica comunque:

```bash
grep -rn "apikey\|token=\|password:" . --exclude-dir=.git
```

Non devono comparire chiavi vere. In particolare la API key di Tomorrow.io in `docs/ha-rest-pioggia.yaml` deve restare `LA_TUA_CHIAVE`.

Gli entity_id restano nel file: non sono segreti, e servono a far capire a chi legge cosa va adattato. Se preferisci, sostituiscili con nomi generici nelle substitution.

## 3. Primo push

```bash
cd percorso/della/cartella
git init -b main
git add .
git commit -m "Display informativo Home Assistant su Apollo M-1"
git remote add origin https://github.com/TUO-UTENTE/esphome-apollo-m1-dashboard.git
git push -u origin main
```

Se e' la prima volta che usi git su questa macchina:

```bash
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua@email"
```

GitHub non accetta piu' la password dell'account via HTTPS: al push ti serve un **personal access token** (Settings → Developer settings → Tokens, scope `repo`) da incollare al posto della password. In alternativa installa GitHub CLI e fai `gh auth login`.

## 4. Rendi il repository utile a chi passa

**Topics** (rotellina accanto a "About"): `esphome`, `home-assistant`, `hub75`, `led-matrix`, `esp32-s3`, `apollo-automation`, `node-red`.

**Description** breve e un link alla foto nel README: su GitHub l'immagine in cima e' quello che fa capire il progetto in due secondi.

**Issues** attive: e' il canale con cui ti arriveranno i suggerimenti.

Un file `CONTRIBUTING.md` non serve per un progetto di questa dimensione. Una sezione "Problemi noti" nel README, che c'e' gia', vale di piu': dice a chi arriva dove puo' essere utile.

## 5. Aggiornamenti successivi

```bash
git add -A
git commit -m "Descrizione della modifica"
git push
```

Quando cambi qualcosa di sostanziale, vale la pena creare un **tag**:

```bash
git tag -a v1.0 -m "Prima versione completa"
git push --tags
```

Cosi' chi usa la tua configurazione puo' tornare a una versione nota se un aggiornamento gli rompe qualcosa.

## 6. Se vuoi aggiungere altre foto

Mettile in `docs/img/` e richiamale nel README con percorso relativo:

```markdown
![Descrizione](docs/img/nome-file.png)
```

Ridimensionale a 1000-1200 px di lato lungo prima di committare: una foto da telefono pesa diversi MB e il repository cresce in fretta.
