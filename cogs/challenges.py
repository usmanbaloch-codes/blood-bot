import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
from database import (
    db, get_user, update_user, increment_user, award_badge
)
from config import COLOR_RED, CURRENCY_EMOJI

challenges_col  = db["challenges"]
user_chall_col  = db["user_challenges"]


class Challenges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /challenge list ───────────────────────────────────────
    @app_commands.command(name="challenges",
                          description="View all active challenges")
    async def challenges_list(self, interaction: discord.Interaction):
        cursor = challenges_col.find({"active": True})
        active = await cursor.to_list(length=50)

        embed = discord.Embed(
            title="💪 Active Challenges",
            color=COLOR_RED,
        )
        if not active:
            embed.description = "No challenges running right now."
        else:
            for c in active:
                embed.add_field(
                    name=f"⚔️ {c['name']}",
                    value=(
                        f"{c['description']}\n"
                        f"**Duration:** {c['days']} days\n"
                        f"**Reward:** {c['reward']} {CURRENCY_EMOJI}"
                    ),
                    inline=False,
                )
        embed.set_footer(text="Use /join <challenge name> to join")
        await interaction.response.send_message(embed=embed)

    # ── /join ─────────────────────────────────────────────────
    @app_commands.command(name="join",
                          description="Join a challenge")
    @app_commands.describe(name="Challenge name")
    async def join(self, interaction: discord.Interaction, name: str):
        challenge = await challenges_col.find_one(
            {"name": {"$regex": name, "$options": "i"}, "active": True}
        )
        if not challenge:
            await interaction.response.send_message(
                f"❌ No active challenge found: **{name}**", ephemeral=True
            )
            return

        existing = await user_chall_col.find_one({
            "user_id":      interaction.user.id,
            "challenge_id": str(challenge["_id"]),
            "completed":    False,
        })
        if existing:
            await interaction.response.send_message(
                "❌ You're already in this challenge!", ephemeral=True
            )
            return

        await user_chall_col.insert_one({
            "user_id":      interaction.user.id,
            "challenge_id": str(challenge["_id"]),
            "name":         challenge["name"],
            "joined":       datetime.now(timezone.utc).isoformat(),
            "checkins":     [],
            "streak":       0,
            "completed":    False,
            "days":         challenge["days"],
            "reward":       challenge["reward"],
        })
        await interaction.response.send_message(
            f"✅ You joined **{challenge['name']}**!\n"
            f"Use `/checkin` daily to track your progress."
        )

    # ── /checkin ─────────────────────────────────────────────
    @app_commands.command(name="checkin",
                          description="Daily challenge check-in")
    async def checkin(self, interaction: discord.Interaction):
        uid = interaction.user.id
        now = datetime.now(timezone.utc)

        cursor = user_chall_col.find({"user_id": uid, "completed": False})
        active = await cursor.to_list(length=10)

        if not active:
            await interaction.response.send_message(
                "❌ You're not in any active challenges. Use `/join`!",
                ephemeral=True,
            )
            return

        messages = []
        for uc in active:
            checkins = uc.get("checkins", [])
            if checkins:
                last = datetime.fromisoformat(checkins[-1])
                if (now - last).total_seconds() < 86400:
                    messages.append(f"⏰ **{uc['name']}** — Already checked in today!")
                    continue

            new_streak = uc.get("streak", 0) + 1
            checkins.append(now.isoformat())

            update = {
                "checkins": checkins,
                "streak":   new_streak,
            }

            # Check completion
            if new_streak >= uc["days"]:
                update["completed"] = True
                user = await get_user(uid)
                await update_user(uid, {
                    "blood_drops":      user["blood_drops"] + uc["reward"],
                    "challenges_done":  user.get("challenges_done", 0) + 1,
                })
                if user.get("challenges_done", 0) + 1 >= 5:
                    await award_badge(uid, "challenge_champion")
                messages.append(
                    f"🏆 **{uc['name']}** — COMPLETED! "
                    f"+{uc['reward']} {CURRENCY_EMOJI}!"
                )
            else:
                remaining = uc["days"] - new_streak
                messages.append(
                    f"✅ **{uc['name']}** — Day {new_streak}/{uc['days']} "
                    f"({remaining} days left)"
                )

            await user_chall_col.update_one(
                {"_id": uc["_id"]}, {"$set": update}
            )

        # ── Update global streak ────────────────────────────
        user = await get_user(uid)
        last_s = user.get("last_streak")
        if last_s:
            diff = (now - datetime.fromisoformat(last_s)).total_seconds()
            if diff < 86400:
                pass
            elif diff < 172800:
                await update_user(uid, {
                    "streak":      user.get("streak", 0) + 1,
                    "last_streak": now.isoformat(),
                })
            else:
                await update_user(uid, {"streak": 1, "last_streak": now.isoformat()})
        else:
            await update_user(uid, {"streak": 1, "last_streak": now.isoformat()})

        if user.get("streak", 0) + 1 >= 7:
            await award_badge(uid, "disciplined")

        embed = discord.Embed(
            title="💪 Check-In Complete",
            description="\n".join(messages) or "Nothing to check in.",
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    # ── /streak ───────────────────────────────────────────────
    @app_commands.command(name="streak",
                          description="View your current daily streak")
    async def streak(self, interaction: discord.Interaction):
        user = await get_user(interaction.user.id)
        streak = user.get("streak", 0)
        embed = discord.Embed(
            title="🔥 Your Streak",
            description=f"Current streak: **{streak} day(s)** 🔥",
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    # ── /createchallenge (admin) ──────────────────────────────
    @app_commands.command(name="createchallenge",
                          description="[ADMIN] Create a new challenge")
    @app_commands.describe(
        name="Challenge name",
        description="What members must do",
        days="Duration in days",
        reward="Blood Drops reward",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def createchallenge(self, interaction: discord.Interaction,
                              name: str, description: str,
                              days: int, reward: int):
        await challenges_col.insert_one({
            "name":        name,
            "description": description,
            "days":        days,
            "reward":      reward,
            "active":      True,
            "created_by":  interaction.user.id,
            "created_at":  datetime.now(timezone.utc).isoformat(),
        })
        await interaction.response.send_message(
            f"✅ Challenge **{name}** created! ({days} days, {reward} {CURRENCY_EMOJI})"
        )

    # ── /endchallenge (admin) ─────────────────────────────────
    @app_commands.command(name="endchallenge",
                          description="[ADMIN] End a challenge")
    @app_commands.describe(name="Challenge name to end")
    @app_commands.checks.has_permissions(administrator=True)
    async def endchallenge(self, interaction: discord.Interaction, name: str):
        result = await challenges_col.update_one(
            {"name": {"$regex": name, "$options": "i"}},
            {"$set": {"active": False}},
        )
        if result.modified_count:
            await interaction.response.send_message(
                f"✅ Challenge **{name}** ended."
            )
        else:
            await interaction.response.send_message(
                f"❌ Challenge not found: **{name}**", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Challenges(bot))