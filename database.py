import motor.motor_asyncio
import certifi
from config import MONGODB_URI, DB_NAME
from datetime import datetime, timezone


# ─── Connection ─────────────────────────────────────────────
# tlsCAFile=certifi.where() fixes "TLSV1_ALERT_INTERNAL_ERROR" on hosts
# whose system cert bundle is out of date (common on Wispbyte / shared
# Docker hosts connecting to MongoDB Atlas).
client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000,
)
db = client[DB_NAME]

# ─── Collections ────────────────────────────────────────────
users_col       = db["users"]
warnings_col    = db["warnings"]
challenges_col  = db["challenges"]
giveaways_col   = db["giveaways"]
quizzes_col     = db["quizzes"]
reminders_col   = db["reminders"]


# ════════════════════════════════════════════════════════════
#  USER HELPERS
# ════════════════════════════════════════════════════════════

async def get_user(user_id: int) -> dict:
    """Fetch user doc, creating one if missing."""
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id":          user_id,
            "xp":               0,
            "level":            0,
            "blood_drops":      0,
            "quiz_wins":        0,
            "challenges_done":  0,
            "streak":           0,
            "last_streak":      None,
            "last_daily":       None,
            "last_xp":          None,
            "bio":              "No bio set.",
            "badges":           [],
            "join_date":        datetime.now(timezone.utc).isoformat(),
            "dhikr_count":      0,
            "total_messages":   0,
        }
        await users_col.insert_one(user)
    return user


async def update_user(user_id: int, update: dict):
    """Apply a $set update to a user doc."""
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": update},
        upsert=True
    )


async def increment_user(user_id: int, field: str, amount: int = 1):
    """Increment a numeric field."""
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {field: amount}},
        upsert=True
    )


async def get_leaderboard(field: str, limit: int = 10) -> list:
    """Return top users sorted by field descending."""
    cursor = users_col.find({}).sort(field, -1).limit(limit)
    return await cursor.to_list(length=limit)


# ════════════════════════════════════════════════════════════
#  WARNING HELPERS
# ════════════════════════════════════════════════════════════

async def add_warning(guild_id: int, user_id: int,
                      mod_id: int, reason: str) -> int:
    await warnings_col.insert_one({
        "guild_id":  guild_id,
        "user_id":   user_id,
        "mod_id":    mod_id,
        "reason":    reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    count = await warnings_col.count_documents(
        {"guild_id": guild_id, "user_id": user_id}
    )
    return count


async def get_warnings(guild_id: int, user_id: int) -> list:
    cursor = warnings_col.find(
        {"guild_id": guild_id, "user_id": user_id}
    )
    return await cursor.to_list(length=100)


async def clear_warnings(guild_id: int, user_id: int):
    await warnings_col.delete_many(
        {"guild_id": guild_id, "user_id": user_id}
    )


# ════════════════════════════════════════════════════════════
#  BADGE HELPER
# ════════════════════════════════════════════════════════════

async def award_badge(user_id: int, badge_key: str):
    """Add badge if not already owned."""
    await users_col.update_one(
        {"user_id": user_id},
        {"$addToSet": {"badges": badge_key}},
        upsert=True
    )