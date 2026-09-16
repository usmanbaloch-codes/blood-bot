import discord
from discord.ext import commands
from discord import app_commands
import asyncio, random
from datetime import datetime, timezone, timedelta
from config import (
    XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX,
    CHAT_XP_COOLDOWN, VC_XP_INTERVAL, VC_XP_PER_TICK,
    VC_AFK_CHANNEL_ID, DAILY_XP_BONUS, DAILY_COINS_BONUS,
    LEVEL_XP, LEVEL_COIN_REWARDS, RANKS,
    CURRENCY_EMOJI, GENERAL_CHANNEL_ID, COLOR_RED,
)
from database import get_user, update_user, award_badge


# ─── Helpers ─────────────────────────────────────────────────
def get_level_from_xp(xp: int) -> int:
    level = 0
    for lvl, req in sorted(LEVEL_XP.items()):
        if xp >= req:
            level = lvl
    return level


def xp_for_next_level(current_level: int) -> int | None:
    levels = sorted(LEVEL_XP.keys())
    for lvl in levels:
        if lvl > current_level:
            return LEVEL_XP[lvl]
    return None


def get_rank(level: int) -> dict:
    rank = RANKS[0]
    for r in RANKS:
        if level >= r["min_level"]:
            rank = r
    return rank


def build_progress_bar(current_xp: int, current_level: int) -> str:
    next_xp = xp_for_next_level(current_level)
    if not next_xp:
        return "`[████████████████████]` MAX"
    cur_req   = LEVEL_XP.get(current_level, 0)
    needed    = next_xp - cur_req
    progress  = current_xp - cur_req
    filled    = int((progress / needed) * 20)
    filled    = max(0, min(20, filled))
    bar       = "█" * filled + "░" * (20 - filled)
    pct       = int((progress / needed) * 100)
    return f"`[{bar}]` {pct}%"


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot            = bot
        self._chat_cd       : dict[int, datetime] = {}
        self._vc_tracking   : dict[int, datetime] = {}
        self._xp_boosts     : dict[int, datetime] = {}
        self._vc_task       = None

    async def cog_load(self):
        self._vc_task = self.bot.loop.create_task(self._vc_xp_loop())

    async def cog_unload(self):
        if self._vc_task:
            self._vc_task.cancel()

    def get_multiplier(self, user_id: int) -> float:
        if user_id in self._xp_boosts:
            if datetime.now(timezone.utc) < self._xp_boosts[user_id]:
                return 2.0
            else:
                del self._xp_boosts[user_id]
        return 1.0

    def apply_boost(self, user_id: int, hours: int):
        expiry = datetime.now(timezone.utc) + timedelta(hours=hours)
        self._xp_boosts[user_id] = expiry

    async def handle_level_up(self, user_id: int,
                               old_level: int, new_level: int,
                               channel: discord.TextChannel | None = None):
        if new_level <= old_level:
            return

        user     = await get_user(user_id)
        total_coins = 0
        for lvl in range(old_level + 1, new_level + 1):
            total_coins += LEVEL_COIN_REWARDS.get(lvl, 10)

        if total_coins > 0:
            await update_user(user_id, {
                "blood_coins": user["blood_coins"] + total_coins
            })

        rank = get_rank(new_level)
        if rank["name"] == "Blood Legend":
            await award_badge(user_id, "blood_legend")

        if channel:
            embed = discord.Embed(
                title="🩸 LEVEL UP!",
                color=rank["color"],
            )
            guild  = channel.guild
            member = guild.get_member(user_id)
            if member:
                embed.set_thumbnail(url=member.display_avatar.url)
                mention = member.mention
            else:
                mention = f"<@{user_id}>"

            embed.description = (
                f"{mention} reached **Level {new_level}**!\n"
                f"{rank['emoji']} **{rank['name']}**\n\n"
                f"🪙 **+{total_coins} {CURRENCY_EMOJI}** Blood Coins awarded!"
            )
            embed.set_footer(text="Keep grinding 🩸")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if len(message.content) < 3:
            return

        uid = message.author.id
        now = datetime.now(timezone.utc)
        last = self._chat_cd.get(uid)
        if last and (now - last).total_seconds() < CHAT_XP_COOLDOWN:
            return

        self._chat_cd[uid] = now
        multi = self.get_multiplier(uid)
        gain  = int(
            random.randint(XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX) * multi
        )

        user      = await get_user(uid)
        old_level = get_level_from_xp(user["xp"])
        new_xp    = user["xp"] + gain
        new_level = get_level_from_xp(new_xp)

        await update_user(uid, {
            "xp":             new_xp,
            "total_messages": user.get("total_messages", 0) + 1,
        })

        if new_level > old_level:
            notif_channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
            await self.handle_level_up(
                uid, old_level, new_level, notif_channel
            )

    async def _vc_xp_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(VC_XP_INTERVAL)
            try:
                for guild in self.bot.guilds:
                    for vc in guild.voice_channels:
                        if vc.id == VC_AFK_CHANNEL_ID:
                            continue
                        active_members = [
                            m for m in vc.members
                            if not m.bot
                            and not m.voice.self_deaf
                            and not m.voice.afk
                        ]
                        if len(active_members) < 1:
                            continue

                        for member in active_members:
                            multi = self.get_multiplier(member.id)
                            gain  = int(VC_XP_PER_TICK * multi)
                            user      = await get_user(member.id)
                            old_level = get_level_from_xp(user["xp"])
                            new_xp    = user["xp"] + gain
                            new_level = get_level_from_xp(new_xp)
                            vc_time = user.get("vc_minutes", 0) + 5
                            await update_user(member.id, {
                                "xp":         new_xp,
                                "vc_minutes": vc_time,
                            })
                            if new_level > old_level:
                                chan = self.bot.get_channel(GENERAL_CHANNEL_ID)
                                await self.handle_level_up(
                                    member.id, old_level, new_level, chan
                                )
            except Exception as e:
                print(f"[VC XP ERROR] {e}")

    @app_commands.command(name="rank", description="View your Blood Rank card")
    async def rank(self, interaction: discord.Interaction,
                   member: discord.Member = None):
        target = member or interaction.user
        user   = await get_user(target.id)
        level  = get_level_from_xp(user["xp"])
        rank   = get_rank(level)
        bar    = build_progress_bar(user["xp"], level)

        next_xp = xp_for_next_level(level)
        cur_xp  = LEVEL_XP.get(level, 0)

        embed = discord.Embed(
            title=f"🩸 {target.display_name} — Blood Rank",
            color=rank["color"],
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🏅 Rank",    value=f"{rank['emoji']} **{rank['name']}**",        inline=True)
        embed.add_field(name="📊 Level",   value=f"**{level}**",                               inline=True)
        embed.add_field(name="⭐ XP",      value=f"**{user['xp']:,}**",                        inline=True)
        embed.add_field(name="🪙 Coins",   value=f"**{user.get('blood_coins', 0):,}** 🪙",    inline=True)
        embed.add_field(name="💬 Messages",value=f"**{user.get('total_messages', 0):,}**",     inline=True)
        embed.add_field(name="🔊 VC Time", value=f"**{user.get('vc_minutes', 0):,} min**",     inline=True)

        if next_xp:
            embed.add_field(
                name=f"Progress to Level {level + 1}",
                value=f"{bar}\n`{user['xp'] - cur_xp:,} / {next_xp - cur_xp:,} XP`",
                inline=False,
            )
        else:
            embed.add_field(name="Progress", value="👑 **MAX LEVEL**", inline=False)

        boost = self._xp_boosts.get(target.id)
        if boost and datetime.now(timezone.utc) < boost:
            embed.add_field(
                name="⚡ XP Boost Active",
                value=f"2x XP until <t:{int(boost.timestamp())}:R>",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard",
                          description="Top 10 members by XP")
    async def leaderboard(self, interaction: discord.Interaction,
                           mode: str = "xp"):
        from database import get_leaderboard
        field  = "xp" if mode != "vc" else "vc_minutes"
        title  = "🩸 XP Leaderboard" if mode != "vc" else "🔊 VC Leaderboard"
        top    = await get_leaderboard(field, 10)

        embed  = discord.Embed(title=title, color=COLOR_RED)
        medals = ["🥇", "🥈", "🥉"]

        for i, u in enumerate(top):
            m     = interaction.guild.get_member(u["user_id"])
            name  = m.display_name if m else f"User {u['user_id']}"
            level = get_level_from_xp(u.get("xp", 0))
            rank  = get_rank(level)
            medal = medals[i] if i < 3 else f"**#{i+1}**"

            if field == "xp":
                val = f"{rank['emoji']} Lv.{level} — **{u.get('xp',0):,} XP**"
            else:
                val = f"**{u.get('vc_minutes',0):,} minutes** in VC"

            embed.add_field(name=f"{medal} {name}", value=val, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="givexp",
                          description="[ADMIN] Give XP to a member")
    @app_commands.checks.has_permissions(administrator=True)
    async def givexp(self, interaction: discord.Interaction,
                     member: discord.Member, amount: int):
        user      = await get_user(member.id)
        old_level = get_level_from_xp(user["xp"])
        new_xp    = user["xp"] + amount
        new_level = get_level_from_xp(new_xp)
        await update_user(member.id, {"xp": new_xp})

        if new_level > old_level:
            chan = self.bot.get_channel(GENERAL_CHANNEL_ID)
            await self.handle_level_up(member.id, old_level, new_level, chan)

        await interaction.response.send_message(
            f"✅ Gave **{amount:,} XP** to {member.mention}. "
            f"Now Level **{new_level}**."
        )


async def setup(bot):
    await bot.add_cog(Leveling(bot))