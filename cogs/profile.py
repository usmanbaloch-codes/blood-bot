import discord
from discord.ext import commands
from discord import app_commands
from config import COLOR_RED, BADGES, CURRENCY_EMOJI
from database import get_user, update_user
from cogs.leveling import get_rank


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /profile ──────────────────────────────────────────────
    @app_commands.command(name="profile",
                          description="View your Blood Profile")
    async def profile(self, interaction: discord.Interaction,
                      member: discord.Member = None):
        target = member or interaction.user
        user   = await get_user(target.id)
        rank   = get_rank(user["xp"])

        # Build badges string
        earned = user.get("badges", [])
        badge_str = " ".join(
            f"{BADGES[b]['emoji']}" for b in earned if b in BADGES
        ) or "No badges yet"

        embed = discord.Embed(
            title=f"🩸 {target.display_name}'s Blood Profile",
            color=rank["color"],
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(
            name="📊 Blood Rank",
            value=f"{rank['emoji']} **{rank['name']}**",
            inline=True,
        )
        embed.add_field(
            name="⭐ XP",
            value=f"**{user['xp']:,}**",
            inline=True,
        )
        embed.add_field(
            name=f"{CURRENCY_EMOJI} Blood Drops",
            value=f"**{user['blood_drops']:,}**",
            inline=True,
        )
        embed.add_field(
            name="🧠 Quiz Wins",
            value=f"**{user.get('quiz_wins', 0)}**",
            inline=True,
        )
        embed.add_field(
            name="💪 Challenges Done",
            value=f"**{user.get('challenges_done', 0)}**",
            inline=True,
        )
        embed.add_field(
            name="🔥 Streak",
            value=f"**{user.get('streak', 0)} days**",
            inline=True,
        )
        embed.add_field(
            name="🏅 Badges",
            value=badge_str,
            inline=False,
        )
        embed.add_field(
            name="📝 Bio",
            value=user.get("bio", "No bio set."),
            inline=False,
        )
        join_date = user.get("join_date", "Unknown")[:10]
        embed.set_footer(text=f"Member since {join_date}")
        await interaction.response.send_message(embed=embed)

    # ── /setbio ───────────────────────────────────────────────
    @app_commands.command(name="setbio",
                          description="Set your profile bio")
    @app_commands.describe(bio="Your new bio (max 150 chars)")
    async def setbio(self, interaction: discord.Interaction, bio: str):
        if len(bio) > 150:
            await interaction.response.send_message(
                "❌ Bio must be 150 characters or less.", ephemeral=True
            )
            return
        await update_user(interaction.user.id, {"bio": bio})
        await interaction.response.send_message(
            f"✅ Bio updated!", ephemeral=True
        )

    # ── /badges ───────────────────────────────────────────────
    @app_commands.command(name="badges",
                          description="View all earnable badges")
    async def badges(self, interaction: discord.Interaction):
        user   = await get_user(interaction.user.id)
        earned = user.get("badges", [])

        embed = discord.Embed(
            title="🏅 All Blood Badges",
            color=COLOR_RED,
        )
        for key, badge in BADGES.items():
            status = "✅" if key in earned else "🔒"
            embed.add_field(
                name=f"{status} {badge['emoji']} {badge['name']}",
                value=badge["desc"],
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))