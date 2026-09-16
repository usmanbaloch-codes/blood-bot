import discord
from discord.ext import commands
from discord import app_commands
from config import COLOR_RED


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /poll ─────────────────────────────────────────────────
    @app_commands.command(name="poll",
                          description="Create a multi-option poll")
    @app_commands.describe(
        question = "Your poll question",
        option1  = "Option A",
        option2  = "Option B",
        option3  = "Option C (optional)",
        option4  = "Option D (optional)",
    )
    async def poll(self, interaction: discord.Interaction,
                   question: str,
                   option1:  str,
                   option2:  str,
                   option3:  str = None,
                   option4:  str = None):
        options  = [o for o in [option1, option2, option3, option4] if o]
        emojis   = ["🇦", "🇧", "🇨", "🇩"]
        embed    = discord.Embed(
            title=f"📊 {question}",
            color=COLOR_RED,
        )
        desc = ""
        for i, opt in enumerate(options):
            desc += f"{emojis[i]} {opt}\n"
        embed.description = desc
        embed.set_footer(
            text=f"Poll by {interaction.user.display_name}"
        )

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])

    # ── /quickpoll ────────────────────────────────────────────
    @app_commands.command(name="quickpoll",
                          description="Quick yes/no poll")
    @app_commands.describe(question="Your yes/no question")
    async def quickpoll(self, interaction: discord.Interaction,
                        question: str):
        embed = discord.Embed(
            title=f"📊 {question}",
            description="✅ Yes  |  ❌ No",
            color=COLOR_RED,
        )
        embed.set_footer(text=f"Poll by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")


async def setup(bot):
    await bot.add_cog(Polls(bot))