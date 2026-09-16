import discord
from discord.ext import commands
from discord import app_commands
import asyncio, random
from datetime import datetime, timezone, timedelta
from config import COLOR_RED
from database import giveaways_col


def parse_time(time_str: str) -> int:
    """Convert '10m', '2h', '1d' to seconds."""
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit  = time_str[-1].lower()
    if unit not in units:
        return 60
    return int(time_str[:-1]) * units[unit]


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /giveaway start ───────────────────────────────────────
    @app_commands.command(name="giveaway",
                          description="Start a giveaway")
    @app_commands.describe(
        prize    = "What you're giving away",
        duration = "Duration e.g. 10m, 2h, 1d",
        winners  = "Number of winners",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway(self, interaction: discord.Interaction,
                       prize: str, duration: str, winners: int = 1):
        seconds  = parse_time(duration)
        end_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

        embed = discord.Embed(
            title="🎁 GIVEAWAY!",
            description=(
                f"**Prize:** {prize}\n"
                f"**Winners:** {winners}\n"
                f"**Ends:** <t:{int(end_time.timestamp())}:R>\n\n"
                f"React with 🎉 to enter!"
            ),
            color=COLOR_RED,
            timestamp=end_time,
        )
        embed.set_footer(text=f"Ends at")
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )

        await interaction.response.send_message("🎉 Giveaway starting!")
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("🎉")

        await giveaways_col.insert_one({
            "message_id": msg.id,
            "channel_id": interaction.channel.id,
            "guild_id":   interaction.guild.id,
            "prize":      prize,
            "winners":    winners,
            "end_time":   end_time.isoformat(),
            "active":     True,
        })

        # ── Auto-end after duration ──────────────────────────
        await asyncio.sleep(seconds)
        await self.end_giveaway(msg.id, interaction.channel, winners, prize)

    async def end_giveaway(self, message_id: int,
                           channel: discord.TextChannel,
                           winners_count: int, prize: str):
        try:
            msg = await channel.fetch_message(message_id)
        except discord.NotFound:
            return

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        if not reaction:
            await channel.send("❌ No reactions found, giveaway cancelled.")
            return

        users = [u async for u in reaction.users() if not u.bot]
        if len(users) < 1:
            await channel.send("❌ No valid entries for the giveaway!")
            return

        winners = random.sample(users, min(winners_count, len(users)))
        winner_mentions = " ".join(w.mention for w in winners)

        embed = discord.Embed(
            title="🎉 GIVEAWAY ENDED",
            description=(
                f"**Prize:** {prize}\n"
                f"**Winner(s):** {winner_mentions}\n\n"
                f"Congratulations! 🩸"
            ),
            color=COLOR_RED,
        )
        await channel.send(embed=embed)
        await giveaways_col.update_one(
            {"message_id": message_id},
            {"$set": {"active": False}},
        )


async def setup(bot):
    await bot.add_cog(Giveaway(bot))