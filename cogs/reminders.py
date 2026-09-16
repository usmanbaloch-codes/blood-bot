import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timezone, timedelta
from database import reminders_col
from config import COLOR_RED


def parse_time_to_seconds(time_str: str) -> int:
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit  = time_str[-1].lower()
    if unit not in units:
        return 60
    return int(time_str[:-1]) * units[unit]


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Restore reminders from DB on restart."""
        now    = datetime.now(timezone.utc)
        cursor = reminders_col.find({"done": False})
        docs   = await cursor.to_list(length=500)
        for doc in docs:
            fire_at = datetime.fromisoformat(doc["fire_at"])
            delay   = (fire_at - now).total_seconds()
            if delay < 0:
                delay = 0
            self.bot.loop.create_task(
                self._fire_reminder(doc, delay)
            )

    async def _fire_reminder(self, doc: dict, delay: float):
        await asyncio.sleep(delay)
        try:
            user = await self.bot.fetch_user(doc["user_id"])
            embed = discord.Embed(
                title="🔔 Reminder!",
                description=doc["text"],
                color=COLOR_RED,
            )
            await user.send(embed=embed)
        except Exception:
            pass
        await reminders_col.update_one(
            {"_id": doc["_id"]}, {"$set": {"done": True}}
        )

    # ── /remind ───────────────────────────────────────────────
    @app_commands.command(name="remind",
                          description="Set a reminder")
    @app_commands.describe(
        time    = "When to remind you e.g. 10m, 2h, 1d",
        message = "What to remind you about",
    )
    async def remind(self, interaction: discord.Interaction,
                     time: str, message: str):
        seconds = parse_time_to_seconds(time)
        fire_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)

        doc = {
            "user_id": interaction.user.id,
            "text":    message,
            "fire_at": fire_at.isoformat(),
            "done":    False,
        }
        await reminders_col.insert_one(doc)
        self.bot.loop.create_task(self._fire_reminder(doc, seconds))

        embed = discord.Embed(
            title="🔔 Reminder Set!",
            description=(
                f"I'll remind you in **{time}**.\n"
                f"**Message:** {message}"
            ),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /reminders ────────────────────────────────────────────
    @app_commands.command(name="reminders",
                          description="View your active reminders")
    async def reminders_list(self, interaction: discord.Interaction):
        cursor = reminders_col.find(
            {"user_id": interaction.user.id, "done": False}
        )
        docs = await cursor.to_list(length=25)
        embed = discord.Embed(
            title="🔔 Your Reminders",
            color=COLOR_RED,
        )
        if not docs:
            embed.description = "No active reminders."
        else:
            for i, doc in enumerate(docs, 1):
                embed.add_field(
                    name=f"#{i}",
                    value=(
                        f"**{doc['text']}**\n"
                        f"Fires: <t:{int(datetime.fromisoformat(doc['fire_at']).timestamp())}:R>"
                    ),
                    inline=False,
                )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminders(bot))