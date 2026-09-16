import discord
from discord.ext import commands
from discord import app_commands
import asyncio, random, json, os
from datetime import datetime, timezone
from config import COLOR_RED, CURRENCY_EMOJI
from database import get_user, update_user, increment_user, award_badge


# ─── Load questions ─────────────────────────────────────────
def load_questions() -> dict:
    path = os.path.join("data", "questions.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    # Default built-in questions
    return {
        "islamic": [
            {
                "q": "How many pillars does Islam have?",
                "a": "5",
                "options": ["3", "4", "5", "6"],
            },
            {
                "q": "Which is the longest Surah in the Quran?",
                "a": "Al-Baqarah",
                "options": ["Al-Baqarah", "Al-Imran", "An-Nisa", "Al-Maidah"],
            },
            {
                "q": "In which month was the Quran revealed?",
                "a": "Ramadan",
                "options": ["Shawwal", "Rajab", "Ramadan", "Dhul Hijjah"],
            },
        ],
        "general": [
            {
                "q": "What is the capital of France?",
                "a": "Paris",
                "options": ["London", "Berlin", "Paris", "Rome"],
            },
            {
                "q": "How many continents are there?",
                "a": "7",
                "options": ["5", "6", "7", "8"],
            },
        ],
        "riddle": [
            {
                "q": "I speak without a mouth. What am I?",
                "a": "An echo",
                "options": ["A shadow", "An echo", "The wind", "A mirror"],
            },
        ],
    }


QUIZ_REWARD   = 50   # Blood Drops per correct answer
QUIZ_TIMEOUT  = 20   # Seconds to answer


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot      = bot
        self.active   : dict[int, bool] = {}  # channel_id: active?
        self.questions = load_questions()

    async def run_quiz(self, interaction: discord.Interaction,
                       category: str):
        channel_id = interaction.channel.id
        if self.active.get(channel_id):
            await interaction.response.send_message(
                "❌ A quiz is already running in this channel!", ephemeral=True
            )
            return

        pool = self.questions.get(category)
        if not pool:
            await interaction.response.send_message(
                f"❌ No questions found for **{category}**.", ephemeral=True
            )
            return

        q_data  = random.choice(pool)
        options = q_data["options"][:]
        random.shuffle(options)
        answer  = q_data["a"].lower()

        embed = discord.Embed(
            title=f"🧠 Quiz — {category.title()}",
            description=q_data["q"],
            color=COLOR_RED,
        )
        letters = ["🇦", "🇧", "🇨", "🇩"]
        for i, opt in enumerate(options):
            embed.add_field(
                name=f"{letters[i]} {opt}",
                value="\u200b",
                inline=True,
            )
        embed.set_footer(text=f"⏰ You have {QUIZ_TIMEOUT} seconds!")

        self.active[channel_id] = True
        await interaction.response.send_message(embed=embed)

        def check(m: discord.Message):
            return (
                m.channel.id == channel_id
                and not m.author.bot
                and m.content.lower() in [o.lower() for o in options]
            )

        try:
            msg = await self.bot.wait_for(
                "message", timeout=QUIZ_TIMEOUT, check=check
            )
            winner = msg.author

            if msg.content.lower() == answer:
                # Award drops
                user = await get_user(winner.id)
                await update_user(winner.id, {
                    "blood_drops": user["blood_drops"] + QUIZ_REWARD,
                    "quiz_wins":   user.get("quiz_wins", 0) + 1,
                })

                wins = user.get("quiz_wins", 0) + 1
                if wins >= 10:
                    await award_badge(winner.id, "quiz_master")

                result_embed = discord.Embed(
                    title="✅ Correct!",
                    description=(
                        f"{winner.mention} got it right!\n"
                        f"**Answer:** {q_data['a']}\n"
                        f"**+{QUIZ_REWARD} {CURRENCY_EMOJI} Blood Drops**"
                    ),
                    color=0x00FF00,
                )
            else:
                result_embed = discord.Embed(
                    title="❌ Wrong!",
                    description=(
                        f"{winner.mention} guessed wrong.\n"
                        f"**Correct Answer:** {q_data['a']}"
                    ),
                    color=COLOR_RED,
                )
            await interaction.channel.send(embed=result_embed)

        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"Nobody answered!\n**Answer:** {q_data['a']}",
                color=0x555555,
            )
            await interaction.channel.send(embed=timeout_embed)
        finally:
            self.active[channel_id] = False

    # ── /quiz ─────────────────────────────────────────────────
    @app_commands.command(name="quiz",
                          description="Start a quiz in this channel")
    @app_commands.describe(
        category="Category: islamic | general | riddle"
    )
    async def quiz(self, interaction: discord.Interaction,
                   category: str = "general"):
        await self.run_quiz(interaction, category.lower())

    # ── /quizleaderboard ─────────────────────────────────────
    @app_commands.command(name="quizleaderboard",
                          description="Top quiz winners")
    async def quizleaderboard(self, interaction: discord.Interaction):
        from database import get_leaderboard
        top = await get_leaderboard("quiz_wins", 10)
        embed = discord.Embed(
            title="🧠 Quiz Leaderboard",
            color=COLOR_RED,
        )
        medals = ["🥇", "🥈", "🥉"]
        for i, u in enumerate(top):
            member = interaction.guild.get_member(u["user_id"])
            name   = member.display_name if member else f"User {u['user_id']}"
            medal  = medals[i] if i < 3 else f"**#{i+1}**"
            embed.add_field(
                name=f"{medal} {name}",
                value=f"**{u.get('quiz_wins', 0)}** wins",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Quiz(bot))