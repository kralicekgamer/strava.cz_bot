# Strava.cz Discord Bot

Tento projekt je jednoduchý Discord bot napsaný v Pythonu, který tě automaticky upozorní na tvé objednávky jídel ze systému [Strava.cz](https://www.strava.cz/).

## Co bot dělá?
Bot funguje tak, že ti pravidelně posílá do soukromých zpráv (DM) přehled tvého jídelníčku na daný den. 

Má nastavené automatické notifikace v tyto časy:
- ☀️ **7:00 (Ranní přehled)** – Pošle ti kompletní přehled toho, co máš ten den objednáno (včetně polévek). Pokud nemáš objednáno nic, napíše ti to.
- 🍲 **13:00 (Obědový přehled)** – Pošle informace o tvém obědě nebo balíčku (pokud ho máš místo oběda), a také o polévce.
- 🌙 **17:00 (Večerní přehled)** – Pošle ti informace o tvé objednané večeři (či druhé večeři).

### Dostupné příkazy:
- `!start` – Registrace uživatele. Bot si uloží tvé Discord ID a začne ti do DM posílat pravidelné notifikace. Zároveň ti hned pošle potvrzovací zprávu.
- `!test` – Slouží k otestování. Bot okamžitě vygeneruje a pošle všechny 3 notifikace (ráno, oběd, večeře).

## Instalace a spuštění

Tato část obsahuje návod, jak bota zprovoznit, aby fungoval neustále na pozadí, a to včetně stažení a instalace. Pro nasazení (Deployment) využijeme jednoduchý nástroj `tmux`.

1. **Instalace závislostí:**
   Připoj se na svůj server a nainstaluj knihovny zapsané v projektu:
   ```bash
   pip install -r requirements.txt
   ```
2. **Nastavení přihlašovacích údajů:**
   Otevři soubor `app.py` a doplň své údaje v sekci "CONFIGURATION":
   - `TOKEN` – Token tvého Discord bota (získáš na Discord Developer Portal).
   - *Nastavení Strava.cz* – Pro přihlášení do `StravaApi` je nutné získat takzvané `SID` a k němu vědět číslo tvé jídelny.
     Podívat se jak vygenerovat SID přes kód můžeš do repozitáře [strava.cz_api](https://github.com/kralicekgamer/strava.cz_api), zkráceně ale stačí použít jejich integrovanou třídu `Sid(uživatelské_jméno, heslo, číslo_jídelny).getSid()` přímo v app.py u konfigurace.
     Případně ho lze získat i manuálně po přihlášení na strava.cz v prohlížeči (v DevTools -> Network -> Cookies najdeš `SID` a vložíš jako string společně s číslem jídelny přímo do `StravaApi()`).
3. **Instalace terminálového nástroje tmux (pokud ještě nemáš):**
   ```bash
   sudo apt install tmux
   ```
4. **Vytvoření izolovaného okna pro bota:**
   Vytvoř novou relaci (session) v tmuxu:
   ```bash
   tmux new -s stravabot
   ```
5. **Spuštění:**
   Přejdi do složky s projektem a klasicky spusť bota:
   ```bash
   cd /cesta/k/tvemu/strava.cz_bot
   python app.py
   ```
6. **Běh na pozadí a testování:**
   Nyní, když bot běží v konzoli, stiskni klávesovou zkratku `Ctrl+B` a hned poté `D`, tím okno bezpečně opustíš, aniž bys bota vypl. Následně můžeš jít na Discord a napsat mu příkaz `!start`.
   
*(Poznámka: Kdykoliv se budeš chtít na běžící okno s botem podívat znovu kvůli logům, napiš: `tmux attach -t stravabot`)*
