import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import json
import os
from datetime import datetime
from api import StravaApi

# --- CONFIGURATION ---
# Replace with your actual Discord Bot Token
# You can also load this from an .env file or environment variable
TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE" 

# Strava.cz Credentials
STRAVA_SESSION = StravaApi(
    "YOUR_STRAVA_CLIENT_ID_HERE", 
    YOUR_STRAVA_CLIENT_SECRET_HERE, 
    "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"
)

# File to store user config (who to DM)
CONFIG_FILE = "config.json"

# --- SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"user_id": None}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

config = load_config()

# --- HELPERS ---

def get_today_meals():
    try:
        # getJidelnicekToday returns a list based on my test
        data = STRAVA_SESSION.getJidelnicekToday()
        if not data:
            return []
        
        # Filter for today just in case, though getJidelnicekToday implies it
        # The API seems to return today's data. 
        # Check datum if needed. API returns "07.01.2026"
        today_str = datetime.now().strftime("%d.%m.%Y")
        
        # Note: API might return slightly different format or future dates?
        # Based on test_api output, it returns a list for the requested context.
        # We will assume the list is relevant for "today" or filter by date string if multiple days present.
        
        return [item for item in data if item.get('datum') == today_str]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Strava.cz Bot")
    return embed

# --- TASKS ---

async def send_dm(message=None, embed=None):
    user_id = config.get("user_id")
    if not user_id:
        print("No user configured to receive messages.")
        return

    user = await bot.fetch_user(user_id)
    if user:
        await user.send(content=message, embed=embed)

async def morning_report():
    """7:00 - Breakfast + Full Menu Summary"""
    print("Running morning report...")
    meals = get_today_meals()
    if not meals:
        await send_dm("Dnes není v jídelníčku nic.")
        return

    # Filter ordered meals
    ordered_meals = [m for m in meals if m.get('pocet', 0) > 0]
    
    # 1. Breakfast (Snídaně) - though sample didn't show it specifically as 'Snídaně' type
    # We'll look for 'Snídaně' in text or type if it exists, otherwise just Summary.
    
    # 2. Summary of whole day
    desc_lines = []
    
    # If there are ordered meals, list them
    if ordered_meals:
        desc_lines.append("**Dnes máš objednáno:**")
        for meal in ordered_meals:
            kind = meal.get('druh_popis', 'Jídlo')
            name = meal.get('nazev', '???')
            desc_lines.append(f"• **{kind}**: {name}")
    else:
        desc_lines.append("Dnes nemáš objednané žádné jídlo.")

    # Also list Soup if available (often not explicitly 'ordered' via count but available)
    soups = [m for m in meals if m.get('druh_popis') == 'Polévka']
    if soups:
        desc_lines.append("\n**Polévka:**")
        for s in soups:
            desc_lines.append(f"• {s.get('nazev')}")

    embed = create_embed("Ranní Přehled", "\n".join(desc_lines), discord.Color.gold())
    await send_dm(embed=embed)

async def lunch_report():
    """13:00 - Lunch (or Package) + Soup"""
    print("Running lunch report...")
    meals = get_today_meals()
    if not meals:
        return

    # Check for Package
    packages = [m for m in meals if (m.get('druh_popis') == 'Balíček' or m.get('druh') == 'BA') and m.get('pocet', 0) > 0]
    
    if packages:
        # Send Package info -> User said "posli balicek misto obedu"
        for p in packages:
             embed = create_embed("Oběd - Balíček", f"**{p.get('nazev')}**", discord.Color.green())
             await send_dm(embed=embed)
    else:
        # Standard Lunch
        lunches = [m for m in meals if m.get('druh_popis') == 'Oběd' and m.get('pocet', 0) > 0]
        soups = [m for m in meals if m.get('druh_popis') == 'Polévka']
        
        if not lunches and not soups:
            # If nothing ordered and no soup, maybe skip? 
            # User said "pokud neco nemam neposilej to".
            return

        embed = discord.Embed(title="Oběd", color=discord.Color.green())
        
        if soups:
            soup_names = "\n".join([f"• {s.get('nazev')}" for s in soups])
            embed.add_field(name="Polévka", value=soup_names, inline=False)
        
        if lunches:
            lunch_names = "\n".join([f"• {l.get('nazev')}" for l in lunches])
            embed.add_field(name="Hlavní chod", value=lunch_names, inline=False)
        else:
             embed.add_field(name="Hlavní chod", value="Nemáš objednáno", inline=False)

        await send_dm(embed=embed)

async def dinner_report():
    """17:00 - Dinner"""
    print("Running dinner report...")
    meals = get_today_meals()
    if not meals:
        return

    dinners = [m for m in meals if m.get('druh_popis') in ['Večeře', 'Druhá večeře'] and m.get('pocet', 0) > 0]
    
    if not dinners:
        return

    desc_lines = []
    for d in dinners:
        desc_lines.append(f"**{d.get('druh_popis')}**: {d.get('nazev')}")

    embed = create_embed("Večeře", "\n".join(desc_lines), discord.Color.purple())
    await send_dm(embed=embed)

# --- COMMANDS ---

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Schedules
    # Note: Times are server time. If server is UTC and user CZ, offset needed.
    # Assuming local time for now or standard cron.
    scheduler.add_job(morning_report, CronTrigger(hour=7, minute=0))
    scheduler.add_job(lunch_report, CronTrigger(hour=13, minute=0))
    scheduler.add_job(dinner_report, CronTrigger(hour=17, minute=0))
    
    scheduler.start()
    print("Scheduler started.")

@bot.command()
async def start(ctx):
    """Registers the user for DMs"""
    # Save the ID of the user who sent the command
    config["user_id"] = ctx.author.id
    save_config(config)
    await ctx.send("Nastaveno! Nyní ti budu posílat jídelníček do DMs.")
    # Send a test immediate DM
    await ctx.author.send("Potvrzuji nastavení. První zpráva přijde v nejbližším termínu (7:00, 13:00, 17:00).")

@bot.command()
async def test(ctx):
    """Force run reports now"""
    await ctx.send("Spouštím test reportů...")
    await morning_report()
    await lunch_report()
    await dinner_report()
    await ctx.send("Test dokončen.")

# Run
if __name__ == "__main__":
    if TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("ERROR: Please set your DISCORD_TOKEN in main.py")
    else:
        bot.run(TOKEN)
