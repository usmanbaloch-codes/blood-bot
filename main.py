import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN, PREFIX, COLOR_RED, GUILD_ID
from database import users_col

# ─── Intents ────────────────────────────────────────────────
intents = discord.Intents.all()

# ─── Bot Setup ──────────────────────────────────────────────
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True,
)

# ─── Cog List ───────────────────────────────────────────────
COGS = [
    "cogs.welcome",
    "cogs.moderation",
    "cogs.economy",
    "cogs.leveling",
    "cogs.quiz",
    "cogs.challenges",
    "cogs.profile",
    "cogs.fun",
    "cogs.giveaway",
    "cogs.polls",
    "cogs.islamic",
    "cogs.reminders",
]


# ─── Events ─────────────────────────────────────────────────
@bot.event
async def on_ready():
    # Sync to your guild (instant). Falls back to global sync if GUILD_ID is 0.
    try:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"[SYNC] {len(synced)} command(s) synced to guild {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"[SYNC] {len(synced)} command(s) synced globally")
    except Exception as e:
        print(f"[SYNC ERROR] {e}")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🩸 BLOOD Server"
        )
    )
    print(f"[BLOOD BOT] Logged in as {bot.user} | {len(bot.guilds)} server(s)")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    # Log every slash command failure so we can see WHY a command "did not respond".
    import traceback
    print(f"[APP CMD ERROR] /{interaction.command.name if interaction.command else '?'}: {error!r}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(f"⚠️ Error: `{error}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Error: `{error}`", ephemeral=True)
    except Exception:
        pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")
        return
    raise error


# ─── Help Command ───────────────────────────────────────────
@bot.hybrid_command(name="help", description="View all bot commands")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🩸 BLOOD Bot — Command Menu",
        color=COLOR_RED
    )
    sections = {
        "🩸 Leveling":    "`/rank` `/leaderboard` `/daily` `/givexp`",
        "💰 Economy":     "`/balance` `/transfer` `/shop` `/buy`",
        "🧠 Quiz":        "`/quiz` `/quizleaderboard`",
        "💪 Challenges":  "`/challenge list` `/challenge join` `/checkin` `/streak`",
        "👤 Profile":     "`/profile` `/setbio` `/badges`",
        "🛡️ Moderation":  "`/warn` `/warnings` `/clot` `/drain` `/purge`",
        "📊 Polls":       "`/poll` `/quickpoll`",
        "🎁 Giveaway":    "`/giveaway`",
        "🕌 Islamic":     "`/pray` `/quran` `/hadith` `/dhikr`",
        "🎭 Fun":         "`/roast` `/8ball` `/coinflip` `/rps` `/joke` `/fact`",
        "🔔 Reminders":   "`/remind` `/reminders`",
    }
    for name, value in sections.items():
        embed.add_field(name=name, value=value, inline=False)
    embed.set_footer(text="🩸 BLOOD Server Bot")
    await ctx.send(embed=embed)


# ─── Startup ────────────────────────────────────────────────
async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"[LOADED] {cog}")
            except Exception as e:
                print(f"[ERROR] Failed to load {cog}: {e}")
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())