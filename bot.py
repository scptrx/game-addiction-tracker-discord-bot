import nextcord
from nextcord.ext import commands
import time
import os
from dotenv import load_dotenv
load_dotenv()

intents = nextcord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_USER_ID = int(os.getenv("MONITORED_USER_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

last_time_not_playing = time.time()
record = 0

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Bot is online')

    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    if target_channel:
        await target_channel.send("Bot is now online.")
    else:
        print("Can't find target channel!")

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("Hello, thanks for adding me! I am ready to monitor gaming (in)activity.")
            return

@bot.event
async def on_presence_update(before, after):
    global last_time_not_playing, record

    if after.id != TARGET_USER_ID:
        return

    playing_before = any(isinstance(a, nextcord.Game) for a in before.activities)
    playing_after = any(isinstance(a, nextcord.Game) for a in after.activities)

    if not playing_before and playing_after:
        now = time.time()
        difference = now - last_time_not_playing
        hours = int(difference // 3600)
        minutes = int((difference % 3600) // 60)

        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if target_channel:
            if difference > record:
                record = difference
                await target_channel.send(
                    f"New record! {after.name} has been away from gaming for {hours} hours and {minutes} minutes!"
                )
        else:
            print(f"Cannot reach channel {TARGET_CHANNEL_ID}")

        last_time_not_playing = time.time()

bot.run(os.getenv("DISCORD_TOKEN"))
