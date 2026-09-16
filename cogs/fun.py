import discord
from discord.ext import commands
from discord import app_commands
import random
from config import COLOR_RED


ROASTS = [
    "You're the human equivalent of a participation trophy.",
    "If laughter is the best medicine, your face must be curing diseases.",
    "You're not stupid; you just have bad luck thinking.",
    "I'd agree with you but then we'd both be wrong.",
    "You have your entire life to be an idiot. Take today off.",
    "I'm not saying I hate you, but I would unplug your life support to charge my phone.",
    "You're proof that even evolution makes mistakes.",
    "Your secrets are always safe with me. I never even listen when you tell me them.",
]

FACTS = [
    "Honey never spoils — archaeologists found 3000-year-old honey in Egypt.",
    "A group of flamingos is called a flamboyance.",
    "Cleopatra lived closer in time to the Moon landing than to the pyramids being built.",
    "The Eiffel Tower can be 15 cm taller in summer due to thermal expansion.",
    "Bananas are curved because they grow towards the sun.",
    "Octopuses have three hearts and blue blood.",
    "A day on Venus is longer than a year on Venus.",
    "The shortest war in history lasted 38–45 minutes.",
]

HALAL_JOKES = [
    "Why don't scientists trust atoms? Because they make up everything! — Just like my excuses for missing Fajr.",
    "I told my mom I wanted to be a comedian. She said 'No son of mine will make people laugh without also making them say Alhamdulillah.'",
    "What do you call a sleeping dinosaur? A dino-snore. What do you call a sleeping Muslim? On time for Tahajjud.",
    "Why did the student eat his homework? Because the teacher told him it was a piece of cake — and cake is halal.",
    "My wife said I never listen... or something like that.",
]

WYR_QUESTIONS = [
    "Would you rather have unlimited money OR unlimited time?",
    "Would you rather always be 10 minutes late OR 20 minutes early?",
    "Would you rather lose your phone OR lose your wallet?",
    "Would you rather live without music OR live without social media?",
    "Would you rather be able to fly OR be invisible?",
]

EIGHT_BALL = [
    "🩸 It is certain.",
    "🩸 Without a doubt.",
    "🩸 Yes, definitely.",
    "🩸 Signs point to yes.",
    "🔴 Reply hazy, try again.",
    "🔴 Cannot predict now.",
    "🔴 Concentrate and ask again.",
    "💀 Don't count on it.",
    "💀 My sources say no.",
    "💀 Outlook not so good.",
]

DARES = [
    "Send a voice message saying 'I am the Blood Legend' in your deepest voice.",
    "Change your nickname to 'Fresh Blood' for 1 hour.",
    "Post your most embarrassing emoji combo.",
    "Write a 2-line poem about this server right now.",
    "Type your next 5 messages in caps lock.",
]

ADVICE = [
    "Success is not given, it is earned — one drop at a time. 🩸",
    "Discipline today = freedom tomorrow.",
    "The strongest person is the one who controls their anger.",
    "Your habits now are your future. Choose wisely.",
    "Pray like it's your last prayer. Work like it's your last day.",
]


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roast", description="Roast someone (all fun!)")
    @app_commands.describe(member="Who to roast")
    async def roast(self, interaction: discord.Interaction,
                    member: discord.Member):
        roast = random.choice(ROASTS)
        await interaction.response.send_message(
            f"🔥 {member.mention}, {roast}"
        )

    @app_commands.command(name="fact", description="Get a random interesting fact")
    async def fact(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💡 Random Fact",
            description=random.choice(FACTS),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="joke", description="Get a halal joke")
    async def joke(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="😄 Halal Joke",
            description=random.choice(HALAL_JOKES),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="wouldyourather",
                          description="Get a Would You Rather question")
    async def wyr(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤔 Would You Rather?",
            description=random.choice(WYR_QUESTIONS),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball",
                          description="Ask the Blood 8-ball a question")
    @app_commands.describe(question="Your question")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(
            title="🎱 Blood 8-Ball",
            color=COLOR_RED,
        )
        embed.add_field(name="Question", value=question,                   inline=False)
        embed.add_field(name="Answer",   value=random.choice(EIGHT_BALL), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["🟡 Heads!", "⚫ Tails!"])
        await interaction.response.send_message(f"🪙 {result}")

    @app_commands.command(name="rps",
                          description="Play Rock Paper Scissors with the bot")
    @app_commands.describe(choice="rock, paper, or scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choices = ["rock", "paper", "scissors"]
        choice  = choice.lower()
        if choice not in choices:
            await interaction.response.send_message(
                "❌ Choose rock, paper, or scissors.", ephemeral=True
            )
            return

        bot_choice = random.choice(choices)
        emojis     = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

        if choice == bot_choice:
            result = "🤝 It's a tie!"
        elif (
            (choice == "rock"     and bot_choice == "scissors") or
            (choice == "paper"    and bot_choice == "rock")     or
            (choice == "scissors" and bot_choice == "paper")
        ):
            result = "🏆 You win!"
        else:
            result = "💀 Bot wins!"

        embed = discord.Embed(
            title="✂️ Rock Paper Scissors",
            color=COLOR_RED,
        )
        embed.add_field(name="You",    value=f"{emojis[choice]} {choice.title()}",     inline=True)
        embed.add_field(name="Bot",    value=f"{emojis[bot_choice]} {bot_choice.title()}", inline=True)
        embed.add_field(name="Result", value=result,                                   inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dare", description="Get a dare")
    async def dare(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="😈 Your Dare",
            description=random.choice(DARES),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="advice", description="Get random life advice")
    async def advice(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💬 Life Advice",
            description=random.choice(ADVICE),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))