# Game Addiction Tracker Discord Bot

Tired of your friend(s) spending endless hours gaming? Now you can track exactly how long they’ve been away from the game and show them who’s really addicted! This bot monitors a user’s game activity and announces new records for the longest non-gaming time directly in your Discord server.

## Features

- Monitors when specific user starts playing a game on Discord
- Tracks the longest period the user was not playing
- Sends notifications in a specific channel when a new non-gaming record is set

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/scptrx/game-addiction-tracker-discord-bot.git
cd game-addiction-tracker-discord-bot
```
### 2. Install dependencies

Make sure you have Python 3.10+ installed.

`pip install nextcord python-dotenv`

### 3. Create a `.env` file

Create a `.env` in the root directory and fill in:

`DISCORD_TOKEN=your_bot_token` 
`MONITORED_USERS=user_id1, user_id2`
`TARGET_CHANNEL_ID=discord_channel_id_for_notifications`

- **DISCORD_TOKEN** – your bot’s token from the Discord Developer Portal
- **MONITORED_USERS** – IDs of users you want to track
- **TARGET_CHANNEL_ID** – the ID of the channel where the bot will send notifications

> How to get IDs: right-click on the user/channel → Copy ID

### 4. Run the bot locally

`python bot.py`

You should see in the console:

`Logged in as YourBotName Bot is online`

The bot will also send a “Bot is now online” message in the target channel.

## Running 24/7

To keep your bot online without leaving your PC on:

- Use a VPS (e.g., [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free?utm_source=chatgpt.com))
- Or a specialized Discord bot host (e.g., [JustRunMy.App](https://justrunmy.app/discord-bots?utm_source=chatgpt.com))

## How to Add Your Bot to a Discord Server

0. **Add your friend(s) to a server**

1. **Go to the Discord Developer Portal**  
    [https://discord.com/developers/applications](https://discord.com/developers/applications)
- Select your bot application.    
- Enable Privileged Intents 
    - Go to Bot → Privileged Gateway Intents
    - Enable **Presence Intent** and **Server Members Intent** and **Message Content Intents**
- **Generate an Invite Link**
    
    - Go to **OAuth2 → URL Generator**
        
    - Under **Scopes**, check `bot`
        
    - Under **Bot Permissions**, check:
        
        - `Send Messages`
            
        - `Read Message History`
            
        - `View Channels`
            
    - Copy the generated URL.
        
- **Invite the Bot**
    
    - Open the URL in your browser
        
    - Choose the server where you have **Manage Server** permission
        
    - Authorize the bot.