# Strava.cz Discord Bot

> ⚠️ **UPOZORNĚNÍ:** Strava.cz má vysoce proměnlivé prostředí (každá jídelna a typ zařízení se může lišit). Z toho důvodu kód tohoto bota i samotné použité API **nejsou plně univerzální**. Tento projekt tak slouží spíše jako dobrá **odrazová šablona**. Pro správné odesílání a parsování dat konkrétní jídelny a konkrétních obědů bude s největší pravděpodobností nutné kód zčásti upravit na míru.

Tento projekt je jednoduchý Discord bot napsaný v Pythonu, který tě automaticky upozorní na tvé objednávky jídel ze systému [Strava.cz](https://www.strava.cz/).

## 🌟 Funkce (Features)

Bot běží na pozadí a zasílá do soukromých zpráv (DM) pravidelný denní přehled:
- ☀️ **7:00 (Ranní přehled)** – Kompletní přehled objednávek na daný den (včetně polévek).
- 🍲 **13:00 (Obědový přehled)** – Informace o obědě, případně balíčku a polévce.
- 🌙 **17:00 (Večerní přehled)** – Informace o objednané večeři (či druhé večeři).

Pokud na daný čas nemáš nic objednáno, bot tě o tom informuje.

## 🛠️ Prerekvizity (Prerequisites)

Před spuštěním budeš potřebovat:
- Nainstalovaný [Python 3.8+](https://www.python.org/downloads/)
- Přihlašovací údaje do portálu Strava.cz (# jídelny, heslo, uživatelské jméno)
- Vytvořenou aplikaci na [Discord Developer Portal](https://discord.com/developers/applications) a její spouštěcí `TOKEN`
- Linuxový server s nástrojem `tmux` (pouze pokud plánuješ online nasazení 24/7)

## ⚙️ Instalace a Konfigurace (Setup)

1. **Stáhnutí a instalace závislostí:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Konfigurace aplikace (`app.py`):**
   Otevři soubor `app.py` a v sekci "CONFIGURATION" doplň své reálné údaje:
   - `TOKEN` – Vlož token tvého Discord bota.
   - **Nastavení Strava.cz:** Pro přihlášení do `StravaApi` je nutné získat takzvané `SID` a k němu vědět číslo tvé jídelny.
     - *Kódově:* Použij třídu `Sid(uživatelské_jméno, heslo, číslo_jídelny).getSid()` z knihovny [strava.cz_api](https://github.com/kralicekgamer/strava.cz_api) přímo v `app.py`.
     - *Manuálně(doporučeno):* Otevři web Strava.cz v prohlížeči, přihlas se a v DevTools (`F12` -> Network/Síť -> Cookies) najdi své `SID`. Tento řetězec vlož do `StravaApi()` jako string.

3. **Lokální spuštění a test:**
   ```bash
   python app.py
   ```
   *Tip: Zamiř na Discord a pošli botovi příkaz `!start`. Pokud se ti potvrdí registrace, vše běží správně a program můžeš vypnout pomocí `Ctrl+C`.*

## 🚀 Nasazení pro běh 24/7 (Deployment)

Pro dlouhodobý běh na Linuxovém serveru se nejčastěji používá izolovaná relace přes terminálový nástroj `tmux`.

1. **Instalace terminálového nástroje tmux (Debian/Ubuntu):**
   ```bash
   sudo apt install tmux
   ```
2. **Vytvoření izolovaného okna pro bota:**
   ```bash
   tmux new -s stravabot
   ```
3. **Spuštění:**
   Uvnitř tmux prostředí přejdi do složky s projektem a bota zapni:
   ```bash
   cd /cesta/k/tvemu/strava.cz_bot
   python app.py
   ```
4. **Běh na pozadí (Odpojení):**
   Stiskni klávesovou zkratku `Ctrl+B` a hned poté `D`. Okno se bezpečně opustí a script zůstane spuštění na pozadí.
5. **Návrat ke konzoli (Logy):**
   Kdykoliv se budeš na okno s instancí chtít podívat znovu, stačí zavolat:
   ```bash
   tmux attach -t stravabot
   ```

## 💻 Použití a Příkazy (Commands)

Jakmile bot získá v konfiguraci přístup, začne reagovat na příkazy v Discordu:
- `!start` – Přihlásí tě k odběru (slouží i jako registrace). Bot si do souboru `config.json` uloží tvé ID uživatele a začne ti v určené časy automaticky zasílat feed.
- `!test` – Force trigger funkcí. Spustí testování notifikací a do DM ti od bota dorazí všechny denní zprávy ihned.

## 📚 Závislosti a Knihovny

Projekt existuje a funguje napojením na následující open-source knihovny:
- [discord.py](https://discordpy.readthedocs.io/en/stable/) – Asynchronní wrapper pro Discord API.
- [APScheduler](https://apscheduler.readthedocs.io/en/3.x/) – Plánovač automatizovaných úloh na pozadí (místo crontab).
- **[strava.cz_api](https://github.com/kralicekgamer/strava.cz_api)** – Neoficiální Python wrapper pro scrapování portálu Strava.cz (získávaní jídla, session cookies).
