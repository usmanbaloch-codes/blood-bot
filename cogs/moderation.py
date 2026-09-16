import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
from config import COLOR_RED, COLOR_DARK, MAX_WARNINGS, LOG_CHANNEL_ID
from database import add_warning, get_warnings, clear_warnings
import humanize


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Log Helper ──────────────────────────────────────────
    async def log_action(self, guild, action, mod, target, reason, color=COLOR_RED):
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if not channel:
            return
        embed = discord.Embed(
            title=f"🛡️ Mod Action — {action}",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Target",    value=target.mention,  inline=True)
        embed.add_field(name="Moderator", value=mod.mention,     inline=True)
        embed.add_field(name="Reason",    value=reason,          inline=False)
        await channel.send(embed=embed)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for warning")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction,
                   member: discord.Member, reason: str = "No reason provided"):
        count = await add_warning(
            interaction.guild.id, member.id,
            interaction.user.id, reason
        )
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            color=COLOR_RED,
        )
        embed.add_field(name="Member",   value=member.mention, inline=True)
        embed.add_field(name="Warnings", value=f"{count}/{MAX_WARNINGS}", inline=True)
        embed.add_field(name="Reason",   value=reason,         inline=False)

        if count >= MAX_WARNINGS:
            embed.add_field(
                name="⚡ Auto-Action",
                value="Max warnings reached! Consider taking further action.",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)
        await self.log_action(
            interaction.guild, "WARN",
            interaction.user, member, reason
        )

    @app_commands.command(name="warnings", description="View a member's warnings")
    @app_commands.describe(member="Member to check")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction,
                       member: discord.Member):
        warns = await get_warnings(interaction.guild.id, member.id)
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.name}",
            color=COLOR_RED,
        )
        if not warns:
            embed.description = "✅ No warnings on record."
        else:
            for i, w in enumerate(warns, 1):
                embed.add_field(
                    name=f"Warning {i}",
                    value=f"**Reason:** {w['reason']}\n**Date:** {w['timestamp'][:10]}",
                    inline=False,
                )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarnings",
                          description="Clear all warnings for a member")
    @app_commands.describe(member="Member to clear")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarnings(self, interaction: discord.Interaction,
                            member: discord.Member):
        await clear_warnings(interaction.guild.id, member.id)
        await interaction.response.send_message(
            f"✅ Cleared all warnings for {member.mention}."
        )

    @app_commands.command(name="clot",
                          description="Temporarily mute a member (Clotted)")
    @app_commands.describe(
        member="Member to clot",
        minutes="Duration in minutes",
        reason="Reason",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clot(self, interaction: discord.Interaction,
                   member: discord.Member,
                   minutes: int = 10,
                   reason: str = "No reason provided"):
        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="🩸 Member Clotted",
            description=(
                f"{member.mention} has been **Clotted** (muted) for "
                f"**{minutes} minute(s)**.\n**Reason:** {reason}"
            ),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)
        await self.log_action(
            interaction.guild, "CLOT (MUTE)",
            interaction.user, member, reason
        )

    @app_commands.command(name="drain", description="Ban a member (Drained)")
    @app_commands.describe(member="Member to drain", reason="Reason")
    @app_commands.checks.has_permissions(ban_members=True)
    async def drain(self, interaction: discord.Interaction,
                    member: discord.Member,
                    reason: str = "No reason provided"):
        embed = discord.Embed(
            title="🩸 Member Drained",
            description=(
                f"**{member.name}** has been **Drained** (banned).\n"
                f"**Reason:** {reason}"
            ),
            color=COLOR_DARK,
        )
        await interaction.response.send_message(embed=embed)
        await member.ban(reason=reason)
        await self.log_action(
            interaction.guild, "DRAIN (BAN)",
            interaction.user, member, reason, color=0x000000
        )

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction,
                   member: discord.Member,
                   reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"👢 {member.mention} has been kicked. Reason: {reason}"
        )
        await self.log_action(
            interaction.guild, "KICK",
            interaction.user, member, reason
        )

    @app_commands.command(name="purge",
                          description="Delete messages in bulk")
    @app_commands.describe(amount="Number of messages to delete (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int = 10):
        amount = min(amount, 100)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(
            f"🗑️ Deleted **{len(deleted)}** message(s).", ephemeral=True
        )

    @app_commands.command(name="lock", description="Lock current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(
            interaction.guild.default_role, send_messages=False
        )
        await interaction.response.send_message(
            "🔒 Channel **locked**."
        )

    @app_commands.command(name="unlock", description="Unlock current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(
            interaction.guild.default_role, send_messages=True
        )
        await interaction.response.send_message(
            "🔓 Channel **unlocked**."
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))