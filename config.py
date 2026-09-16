import os
from dotenv import load_dotenv

load_dotenv()

# ─── Environment / Secrets ──────────────────────────────────
TOKEN              = os.getenv("TOKEN")
MONGODB_URI        = os.getenv("MONGODB_URI")
DB_NAME            = os.getenv("DB_NAME", "bloodbot")
PREFIX             = os.getenv("PREFIX", "$")
GUILD_ID           = int(os.getenv("GUILD_ID", "0") or 0)
LOG_CHANNEL_ID     = int(os.getenv("LOG_CHANNEL_ID", "0") or 0)
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0") or 0)
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID", "0") or 0)

if not TOKEN:
    raise RuntimeError("TOKEN is missing. Set it in your .env file.")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is missing. Set it in your .env file.")

# ─── Colors ─────────────────────────────────────────────────
COLOR_RED  = 0xFF0000
COLOR_DARK = 0x1A0000

# ─── Moderation ─────────────────────────────────────────────
MAX_WARNINGS = 3

# ─── Badges ─────────────────────────────────────────────────
BADGES = {
    "og":            {"emoji": "🩸", "name": "OG Member"},
    "level_10":      {"emoji": "🔟", "name": "Level 10"},
    "level_25":      {"emoji": "🥈", "name": "Level 25"},
    "level_50":      {"emoji": "🥇", "name": "Level 50"},
    "quiz_master":   {"emoji": "🧠", "name": "Quiz Master"},
    "challenger":    {"emoji": "💪", "name": "Challenger"},
    "streak_7":      {"emoji": "🔥", "name": "7-Day Streak"},
    "streak_30":     {"emoji": "⚡", "name": "30-Day Streak"},
    "rich":          {"emoji": "💰", "name": "Rich Blood"},
    "vip":           {"emoji": "💎", "name": "VIP"},
}

# ─── Daily Bonus Alias ──────────────────────────────────────
DAILY_DROPS_BONUS = 100  # Blood Coins per /daily

# ─── XP Settings ────────────────────────────────────────────
XP_PER_MESSAGE_MIN  = 5
XP_PER_MESSAGE_MAX  = 10
CHAT_XP_COOLDOWN    = 90       # Seconds between XP gains from chat
VC_XP_INTERVAL      = 300      # 5 minutes in VC = XP tick
VC_XP_PER_TICK      = 8        # XP per 5 min in VC
VC_AFK_CHANNEL_ID   = 0        # Set your AFK channel ID
DAILY_XP_BONUS      = 50
DAILY_COINS_BONUS   = 100

# ─── Level Thresholds ────────────────────────────────────────
LEVEL_XP = {
    1: 100,    2: 250,    3: 450,    4: 700,
    5: 1000,   6: 1400,   7: 1900,   8: 2500,
    9: 3200,   10: 4000,  11: 5000,  12: 6200,
    13: 7600,  14: 9200,  15: 11000, 16: 13200,
    17: 15700, 18: 18500, 19: 21700, 20: 25300,
    25: 40000, 30: 65000, 40: 120000,50: 200000,
}

LEVEL_COIN_REWARDS = {
    1: 25,   2: 30,   3: 40,   4: 50,
    5: 75,   6: 80,   7: 90,   8: 100,
    9: 110,  10: 200, 15: 350, 20: 600,
    25: 900, 30: 1500,40: 2500,50: 5000,
}

# ─── Blood Rank Thresholds (by LEVEL not XP) ────────────────
RANKS = [
    {"name": "Fresh Blood",  "emoji": "🩸", "min_level": 0,  "color": 0xFF0000},
    {"name": "Blood Born",   "emoji": "💉", "min_level": 5,  "color": 0xCC0000},
    {"name": "Pure Blood",   "emoji": "🔴", "min_level": 10, "color": 0xAA0000},
    {"name": "Blood Knight", "emoji": "⚔️", "min_level": 20, "color": 0x880000},
    {"name": "Blood Warden", "emoji": "🛡️", "min_level": 30, "color": 0x660000},
    {"name": "Blood Legend", "emoji": "👑", "min_level": 40, "color": 0x440000},
]

# ─── Economy ─────────────────────────────────────────────────
CURRENCY_NAME  = "Blood Coins"
CURRENCY_EMOJI = "🪙"

# ─── Game Rewards (Blood Coins) ──────────────────────────────
GAME_REWARDS = {
    "blackjack_win":     80,
    "blackjack_lose":    0,
    "slots_jackpot":     500,
    "slots_win":         60,
    "slots_lose":        0,
    "trivia_win":        50,
    "rps_win":           30,
    "scramble_win":      40,
    "hangman_win":       45,
    "coinflip_win":      35,
    "roulette_win":      100,
    "connectfour_win":   75,
    "tictactoe_win":     40,
    "race_win":          90,
    "numberguess_win":   35,
}

# ─── Shop Items ──────────────────────────────────────────────
SHOP_ITEMS = {
    "color_red":      {"name": "🔴 Red Name",         "price": 500,  "type": "role"},
    "vip":            {"name": "💎 VIP Access",        "price": 2000, "type": "role"},
    "nickname":       {"name": "✏️ Nickname Change",   "price": 300,  "type": "service"},
    "custom_role":    {"name": "🎭 Custom Role Color", "price": 1000, "type": "service"},
    "secret_channel": {"name": "🔓 Secret Channel",   "price": 3000, "type": "role"},
    "xp_boost_1h":   {"name": "⚡ 1h XP Boost x2",   "price": 400,  "type": "boost"},
    "xp_boost_24h":  {"name": "⚡ 24h XP Boost x2",  "price": 1500, "type": "boost"},
    "og_badge":       {"name": "🩸 OG Badge",          "price": 5000, "type": "badge"},
}