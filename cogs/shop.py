import discord
from discord.ext import commands
from discord import app_commands
from config import COLOR_RED, CURRENCY_EMOJI, SHOP_ITEMS
from database import get_user, update_user, award_badge
from datetime import datetime, timezone, timedelta


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop",
                          description="Browse the Blood Coin shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🛒 Blood Shop — Spend your {CURRENCY_EMOJI}",
            description=(
                "Use `/buy <item_id>` to purchase.\n"
                "Blood Coins are earned by gaming, leveling and daily claims."
            ),
            color=COLOR_RED,
        )
        for item_id, item in SHOP_ITEMS.items():
            embed.add_field(
                name=f"{item['name']} — {item['price']:,} {CURRENCY_EMOJI}",
                value=f"`/buy {item_id}`",
                inline=False,
            )
        user = await get_user(interaction.user.id)
        embed.set_footer(
            text=f"Your balance: {user.get('blood_coins', 0):,} 🪙"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy",
                          description="Buy an item from the Blood Shop")
    @app_commands.describe(item_id="Item ID from /shop")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        item = SHOP_ITEMS.get(item_id.lower())
        if not item:
            await interaction.response.send_message(
                f"❌ Item `{item_id}` not found. Check `/shop`.",
                ephemeral=True,
            )
            return

        user = await get_user(interaction.user.id)
        bal  = user.get("blood_coins", 0)

        if bal < item["price"]:
            await interaction.response.send_message(
                f"❌ Need **{item['price']:,}** 🪙 — You have **{bal:,}** 🪙",
                ephemeral=True,
            )
            return

        await update_user(interaction.user.id, {
            "blood_coins": bal - item["price"]
        })

        if item["type"] == "boost":
            hours = 1 if "1h" in item_id else 24
            lev_cog = self.bot.get_cog("Leveling")
            if lev_cog:
                lev_cog.apply_boost(interaction.user.id, hours)
            msg = f"⚡ **XP Boost** active for {hours} hour(s)!"

        elif item["type"] == "badge":
            await award_badge(interaction.user.id, "og_badge")
            msg = "🩸 **OG Badge** added to your profile!"

        elif item["type"] == "role":
            role_map = {
                "color_red":      0,
                "vip":            0,
                "secret_channel": 0,
            }
            role_id = role_map.get(item_id)
            if role_id:
                role = interaction.guild.get_role(role_id)
                if role:
                    await interaction.user.add_roles(role)
            msg = f"✅ **{item['name']}** has been applied to your account!"

        else:
            msg = (
                f"✅ Purchased **{item['name']}**!\n"
                f"A staff member will apply this manually."
            )

        embed = discord.Embed(
            title="✅ Purchase Successful",
            description=(
                f"**Item:** {item['name']}\n"
                f"**Cost:** {item['price']:,} 🪙\n"
                f"**Remaining:** {bal - item['price']:,} 🪙\n\n"
                f"{msg}"
            ),
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="balance",
                          description="Check Blood Coin balance")
    async def balance(self, interaction: discord.Interaction,
                      member: discord.Member = None):
        target = member or interaction.user
        user   = await get_user(target.id)
        embed  = discord.Embed(
            title=f"🪙 {target.display_name}'s Blood Coins",
            description=f"**{user.get('blood_coins', 0):,}** 🪙",
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Shop(bot))