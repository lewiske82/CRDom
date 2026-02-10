# Telepítés és üzemeltetés macOS (Mac mini)

Ez a leírás egy egyszerű, biztonságos, helyi telepítési folyamatot ad a CRDom (AI CRM) alkalmazáshoz macOS-en (Mac mini).

## Előfeltételek

- **macOS 12+** (javasolt: legújabb stabil)
- **Git**
- **Node.js 18+** (nvm-mel ajánlott)
- **Python 3.11+** (ha a projektben Python szolgáltatás is van)
- **Docker Desktop** (opcionális, ha konténereket használtok)

## 1) Projekt letöltése

```bash
git clone <REPO_URL>
cd CRDom
```

## 2) Környezeti változók beállítása

Hozz létre egy helyi `.env` fájlt (ha a projekt használ ilyet), és töltsd ki a szükséges kulcsokat.

```bash
cp .env.example .env
```

**Fontos:** érzékeny kulcsokat ne commitolj.

## 3) Függőségek telepítése

### Node.js

```bash
npm install
```

### Python (ha szükséges)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Adatbázis / háttérszolgáltatások

Ha a projekt adatbázist igényel, indítsd el a helyi szolgáltatásokat (pl. Dockerrel).

```bash
# példa
# docker compose up -d
```

## 5) Lokális futtatás

```bash
npm run dev
```

Ha külön backend indul:

```bash
# példa
# npm run server
```

## 6) macOS szolgáltatásként futtatás (launchd)

Hozz létre egy launchd plist-et, hogy a CRM újrainduljon reboot után is.

1. Minta plist fájl: `~/Library/LaunchAgents/com.crdom.local.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.crdom.local</string>

    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>-lc</string>
      <string>cd /Users/<USER>/CRDom && npm run start</string>
    </array>

    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/<USER>/Library/Logs/crdom.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/<USER>/Library/Logs/crdom.err.log</string>
  </dict>
</plist>
```

2. Betöltés:

```bash
launchctl load ~/Library/LaunchAgents/com.crdom.local.plist
launchctl start com.crdom.local
```

3. Leállítás:

```bash
launchctl stop com.crdom.local
launchctl unload ~/Library/LaunchAgents/com.crdom.local.plist
```

## 7) Hálózati elérés (opcionális)

Ha a CRM-et a helyi hálózaton is el akarod érni:

- Állíts be **statikus IP-t** a Mac mini-nek.
- A tűzfalon engedélyezd a használt portot (pl. 3000).
- Routeren port forward (ha internet felől is kell, csak VPN-nel javasolt).

## 8) Frissítés

```bash
git pull
npm install
npm run build
launchctl restart com.crdom.local
```

## 9) Gyakori hibák

- **Port foglalt**: ellenőrizd, hogy nincs másik szolgáltatás a 3000-es porton.
- **Jogosultsági hiba**: nézd meg a logokat: `~/Library/Logs/crdom.err.log`.

---

Ha szeretnéd, kiegészítem konkrét stackre (pl. Firebase, MySQL, WordPress, stb.) szabott telepítéssel is.
