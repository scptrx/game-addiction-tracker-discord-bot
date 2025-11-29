from datetime import datetime
import nextcord
from nextcord.ext import commands
import time
import os
from dotenv import load_dotenv
load_dotenv()
import json

intents = nextcord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

MONITORED_USERS = [int(uid) for uid in os.getenv("MONITORED_USERS", "").split(",") if uid.strip().isdigit()]
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

user_state = {
    uid: {
        "last_time_not_playing": time.time(),
        "record": 0
    }
    for uid in MONITORED_USERS
}

BREAKS_FILE = "breaks.json"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

SESSION_LOG_FILE = os.path.join(
    LOG_DIR, f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

def _load_breaks():
    try:
        if not os.path.exists(BREAKS_FILE):
            with open(BREAKS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        with open(BREAKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except (json.JSONDecodeError, IOError):
        data = []
        try:
            with open(BREAKS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        except IOError:
            pass
    return data

breaks_data = _load_breaks()

for uid in MONITORED_USERS:
    max_seconds = user_state[uid].get("record", 0)
    for b in breaks_data:
        try:
            if b.get("user_id") == uid:
                mins = int(b.get("duration_minutes", 0))
                secs = max(0, mins * 60)
                if secs > max_seconds:
                    max_seconds = secs
        except (TypeError, ValueError):
            continue
    user_state[uid]["record"] = max_seconds

        
def save_break(user_id, username, start_time, end_time, duration_seconds):
    with open(BREAKS_FILE, "r") as f:
        data = json.load(f)

    data.append({
        "user_id": user_id,
        "username": username,
        "start": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
        "end": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": int(duration_seconds // 60)
    })

    with open(BREAKS_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
        
def log(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"

    print(line)

    with open(SESSION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Bot is online.')

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    
    if channel:
        await channel.send("Bot is now online.")

        usernames = []
        for user_id in MONITORED_USERS:
            user = await bot.fetch_user(user_id)
            usernames.append(user.name)

        users_txt = ", ".join(usernames)
        await channel.send(f"Monitoring users: {users_txt}")
    else:
        print("Can't find target channel!")

@bot.event
async def on_presence_update(before, after):

    log(f"Presence update detected: {after} | ID {after.id}")
    if after.id not in MONITORED_USERS:
        log("User is not monitored, ignoring.")
        return
    
    state = user_state[after.id]

    log(f"Activities BEFORE: {[str(a) for a in before.activities]}")
    log(f"Activities AFTER: {[str(a) for a in after.activities]}")

    playing_before = any(a.type == nextcord.ActivityType.playing for a in before.activities)
    playing_after = any(a.type == nextcord.ActivityType.playing for a in after.activities)

    log(f"playing_before={playing_before}, playing_after={playing_after}")
    
    if not playing_before and playing_after:
        log(f"{after.name} started playing a game. Calculating break...")
        
        now = time.time()
        last_time_not_playing = state["last_time_not_playing"]
        difference = now - last_time_not_playing
        
        hours = int(difference // 3600)
        minutes = int((difference % 3600) // 60)
        
        log(f"Break length: {difference}s, which is {hours}h {minutes}m")
        save_break(after.id, after.name, last_time_not_playing, now, difference)

        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        
        log(f"Channel resolved: {target_channel}. Record so far: {state['record']}")

        if target_channel and difference > state["record"]:
                state["record"] = difference
                log("This is a new record. Sending Discord message.")
                await target_channel.send(
                    f"New record! {after.name} has been away from gaming for {hours} hours and {minutes} minutes!")

    if playing_before and not playing_after:
        log(f"{after.name} stopped playing. Setting last_time_not_playing.")
        state["last_time_not_playing"] = time.time()

        
@bot.command()
async def stats(ctx):

    if not os.path.exists(BREAKS_FILE):
        await ctx.send("No stats yet!")
        return

    with open(BREAKS_FILE, "r") as f:
        data = json.load(f)

    if not data:
        await ctx.send("No breaks recorded yet!")
        return

    msg = "**Break history:**\n"

    for b in data[-50:]:
        msg += (
            f"\nUser: {b['username']}\n"
            f"Start: {b['start']}\n"
            f"End: {b['end']}\n"
            f"Duration: {b['duration_minutes']} minutes\n"
        )

    await ctx.send(msg)
    
@bot.command()
async def records(ctx):
    msg = "**Current Records:**"
    for uid in MONITORED_USERS:
        user = await bot.fetch_user(uid)
        record_seconds = user_state[uid]["record"]
        hours = int(record_seconds // 3600)
        minutes = int((record_seconds % 3600) // 60)
        msg += f"\n{user.name}: {hours} hours and {minutes} minutes"
    
    await ctx.send(msg)
    
@bot.command()
async def helpme(ctx):
    help_text = (
        "**Game Addiction Tracker Bot Commands:**\n"
        "`!stats` - Show the history of breaks taken by monitored users.\n"
        "`!records` - Show the current non-gaming records for monitored users.\n"
        "`!helpme` - Display this help message.\n"
    )
    await ctx.send(help_text)

bot.run(os.getenv("DISCORD_TOKEN"))
