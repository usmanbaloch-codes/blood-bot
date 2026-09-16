# 🩸 BLOOD — Multipurpose Discord Bot

A feature-rich multipurpose Discord bot built with **Python** and **discord.py**. BLOOD combines moderation, leveling, economy, community tools, Islamic utilities, profiles, challenges, quizzes, reminders, giveaways and entertainment features in one modular bot.

> This public repository intentionally excludes private credentials. Create your own `.env` file from `.env.example` before running the bot.

## ✨ Features

- **Moderation** — warnings, warning history, clear warnings, timeouts, bans, kicks, purge, channel lock/unlock and moderation logging.
- **Leveling** — chat XP, voice XP, levels, rank cards, leaderboards and admin XP controls.
- **Economy** — balances, daily rewards, transfers, a virtual shop and richest-member leaderboard.
- **Profiles & badges** — user profiles, bios, ranks and achievement badges.
- **Quizzes & challenges** — interactive quizzes, challenge participation, check-ins and streak tracking.
- **Community tools** — polls, giveaways, reminders and welcome/leave messages.
- **Islamic utilities** — Qur'an lookup, prayer times, dhikr, quotes and hadith commands.
- **Fun commands** — jokes, facts, 8-ball, rock-paper-scissors, dares, advice and more.
- **Modular architecture** — features are organized into cogs for easier maintenance and expansion.

## 🧰 Tech Stack

- Python
- discord.py 2.x
- MongoDB / Motor
- aiohttp
- Pillow
- python-dotenv

## 📁 Project Structure

```text
.
├── cogs/           # Bot feature modules
├── data/           # JSON data used by features
├── utils/          # Shared helper modules
├── config.py       # Environment + bot configuration
├── database.py     # MongoDB access helpers
├── main.py         # Bot startup and cog loading
├── requirements.txt
└── .env.example
```

## 🚀 Setup

1. Install **Python 3.11+**.
2. Create a Discord application/bot and enable the intents your server needs.
3. Create a MongoDB database.
4. Clone this repository and install dependencies:

```bash
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env` and add your own values:

```env
TOKEN=your_discord_bot_token_here
MONGODB_URI=your_mongodb_connection_string_here
DB_NAME=bloodbot
PREFIX=$
GUILD_ID=0
LOG_CHANNEL_ID=0
WELCOME_CHANNEL_ID=0
GENERAL_CHANNEL_ID=0
```

6. Start the bot:

```bash
python main.py
```

Setting `GUILD_ID` to a server ID makes slash-command syncing faster during development. Leave it as `0` to use global syncing.

## 💬 Main Command Categories

| Category | Example commands |
| --- | --- |
| Moderation | `/warn`, `/warnings`, `/clot`, `/drain`, `/kick`, `/purge`, `/lock` |
| Leveling | `/rank`, `/leaderboard`, `/givexp` |
| Economy | `/balance`, `/daily`, `/transfer`, `/shop`, `/richest` |
| Quiz | `/quiz`, `/quizleaderboard` |
| Challenges | `/challenges`, `/join`, `/checkin`, `/streak` |
| Profile | `/profile`, `/setbio`, `/badges` |
| Polls | `/poll`, `/quickpoll` |
| Giveaways | `/giveaway` |
| Islamic | `/quran`, `/pray`, `/dhikr`, `/quote`, `/hadith` |
| Fun | `/roast`, `/fact`, `/joke`, `/wouldyourather`, `/8ball`, `/rps`, `/dare` |
| Reminders | `/remind`, `/reminders` |

## 🔐 Security

Never commit your `.env` file, Discord bot token, MongoDB URI or private server credentials. If a credential is ever exposed publicly, rotate it immediately.

## 📝 Notes

The source also contains additional/experimental modules that can be enabled or adapted as the bot grows. Check command names for conflicts before loading extra cogs together.
