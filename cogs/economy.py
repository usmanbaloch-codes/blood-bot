import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
from config import COLOR_RED, CURRENCY_EMOJI, CURRENCY_NAME, DAILY_DROPS_BONUS
from database import get_user, update_user, increment_user, get_leaderboard


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /balance ─────────────────────────────────────────────
    @app_commands.command(name="balance",
                          description="Check your Blood Drops balance")
    async def balance(self, interaction: discord.Interaction,
                      member: discord.Member = None):
        target = member or interaction.user
        user = await get_user(target.id)
        embed = discord.Embed(
            title=f"{CURRENCY_EMOJI} Blood Drops Balance",
            description=(
                f"{target.mention} has "
                f"**{user['blood_drops']:,} {CURRENCY_EMOJI} Blood Drops**"
            ),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    # ── /daily ───────────────────────────────────────────────
    @app_commands.command(name="daily",
                          description="Claim your daily Blood Drops + XP")
    async def daily(self, interaction: discord.Interaction):
        user = await get_user(interaction.user.id)
        now = datetime.now(timezone.utc)

        if user.get("last_daily"):
            last = datetime.fromisoformat(user["last_daily"])
            diff = now - last
            if diff < timedelta(hours=24):
                remaining = timedelta(hours=24) - diff
                h, m = divmod(int(remaining.total_seconds()), 3600)
                m //= 60
                await interaction.response.send_message(
                    f"⏰ Daily already claimed! Come back in "
                    f"**{h}h {m}m**.", ephemeral=True
                )
                return

        from config import DAILY_XP_BONUS
        new_drops = user["blood_drops"] + DAILY_DROPS_BONUS
        new_xp    = user["xp"] + DAILY_XP_BONUS
        await update_user(interaction.user.id, {
            "blood_drops": new_drops,
            "xp":          new_xp,
            "last_daily":  now.isoformat(),
        })

        embed = discord.Embed(
            title="🩸 Daily Claimed!",
            description=(
                f"You received:\n"
                f"**{DAILY_DROPS_BONUS} {CURRENCY_EMOJI} Blood Drops**\n"
                f"**{DAILY_XP_BONUS} XP**\n\n"
                f"New Balance: **{new_drops:,} {CURRENCY_EMOJI}**"
            ),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    # ── /transfer ────────────────────────────────────────────
    @app_commands.command(name="transfer",
                          description="Send Blood Drops to another member")
    @app_commands.describe(
        member="Who to send to",
        amount="Amount to send",
    )
    async def transfer(self, interaction: discord.Interaction,
                       member: discord.Member, amount: int):
        if member.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You can't transfer to yourself.", ephemeral=True
            )
            return
        if amount <= 0:
            await interaction.response.send_message(
                "❌ Amount must be positive.", ephemeral=True
            )
            return

        sender = await get_user(interaction.user.id)
        if sender["blood_drops"] < amount:
            await interaction.response.send_message(
                f"❌ You only have **{sender['blood_drops']:,} "
                f"{CURRENCY_EMOJI}**.", ephemeral=True
            )
            return

        await update_user(interaction.user.id,
                          {"blood_drops": sender["blood_drops"] - amount})
        receiver = await get_user(member.id)
        await update_user(member.id,
                          {"blood_drops": receiver["blood_drops"] + amount})

        embed = discord.Embed(
            title=f"{CURRENCY_EMOJI} Transfer Successful",
            description=(
                f"{interaction.user.mention} sent "
                f"**{amount:,} {CURRENCY_EMOJI}** to {member.mention}!"
            ),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    # ── /shop ────────────────────────────────────────────────
    @app_commands.command(name="shop", description="View the Blood Shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🛒 Blood Shop — Spend your {CURRENCY_EMOJI}",
            color=COLOR_RED,
        )
        items = [
            ("🔴 Red Name Role",      "500 🩸",  "Custom red name color"),
            ("🩸 VIP Access",         "1000 🩸", "Access to VIP channel"),
            ("✏️ Nickname Change",    "200 🩸",  "Change your server nickname"),
            ("🎭 Custom Role Color",  "750 🩸",  "Pick your role color"),
            ("🔓 Secret Channel",     "2000 🩸", "Access secret server channel"),
        ]
        for name, price, desc in items:
            embed.add_field(
                name=f"{name} — {price}",
                value=desc,
                inline=False,
            )
        embed.set_footer(text="Use /buy [item name] to purchase")
        await interaction.response.send_message(embed=embed)

    # ── /leaderboard economy ─────────────────────────────────
    @app_commands.command(name="richest",
                          description="Top 10 richest members")
    async def richest(self, interaction: discord.Interaction):
        top = await get_leaderboard("blood_drops", 10)
        embed = discord.Embed(
            title=f"💰 Richest Members — Blood Drops",
            color=COLOR_RED,
        )
        medals = ["🥇", "🥈", "🥉"]
        for i, u in enumerate(top):
            member = interaction.guild.get_member(u["user_id"])
            name   = member.display_name if member else f"User {u['user_id']}"
            medal  = medals[i] if i < 3 else f"**#{i+1}**"
            embed.add_field(
                name=f"{medal} {name}",
                value=f"{u['blood_drops']:,} {CURRENCY_EMOJI}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    # ── Admin: /adddrops ─────────────────────────────────────
    @app_commands.command(name="adddrops",
                          description="[ADMIN] Add Blood Drops to a member")
    @app_commands.describe(member="Target member", amount="Amount to add")
    @app_commands.checks.has_permissions(administrator=True)
    async def adddrops(self, interaction: discord.Interaction,
                       member: discord.Member, amount: int):
        user = await get_user(member.id)
        new_total = user["blood_drops"] + amount
        await update_user(member.id, {"blood_drops": new_total})
        await interaction.response.send_message(
            f"✅ Added **{amount:,} {CURRENCY_EMOJI}** to "
            f"{member.mention}. New balance: **{new_total:,}**"
        )


async def setup(bot):
    await bot.add_cog(Economy(bot))