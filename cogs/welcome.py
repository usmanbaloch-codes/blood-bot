import discord
from discord.ext import commands
from config import WELCOME_CHANNEL_ID, COLOR_RED
from database import get_user
from datetime import datetime, timezone


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # ── Ensure user doc exists ──────────────────────────
        await get_user(member.id)

        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🩸 A NEW DROP HAS JOINED",
            description=(
                f"Welcome to **BLOOD Server**, {member.mention}!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🩸 **You are Fresh Blood**\n"
                "Chat to earn XP and rise through the ranks.\n\n"
                "📜 Read the rules before anything else.\n"
                "💰 Claim your daily Blood Drops with `/daily`\n"
                "🧠 Test yourself with `/quiz`\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=COLOR_RED,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(
            text=f"Member #{member.guild.member_count}"
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🩸 A DROP HAS LEFT",
            description=(
                f"**{member.name}** has left the server.\n"
                f"Members remaining: **{member.guild.member_count}**"
            ),
            color=0x333333,
        )
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))