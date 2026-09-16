import discord
from discord.ext import commands
from discord import app_commands
import aiohttp, random
from config import COLOR_RED
from database import get_user, update_user, award_badge

DHIKR_LIST = [
    "سُبْحَانَ اللَّهِ — SubhanAllah (Glory be to Allah)",
    "الْحَمْدُ لِلَّهِ — Alhamdulillah (All praise is for Allah)",
    "اللَّهُ أَكْبَرُ — Allahu Akbar (Allah is the Greatest)",
    "لَا إِلَهَ إِلَّا اللَّهُ — La ilaha illallah (There is no god but Allah)",
    "أَسْتَغْفِرُ اللَّهَ — Astaghfirullah (I seek forgiveness from Allah)",
    "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ — La hawla wala quwwata illa billah",
    "صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ — Sallallahu alayhi wa sallam",
    "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ — Bismillah ir-Rahman ir-Raheem",
]

ISLAMIC_QUOTES = [
    "Whoever fears Allah, Allah will find him a way out. — Quran 65:2",
    "Indeed, with hardship comes ease. — Quran 94:6",
    "The best of you are those who are best to their families. — Hadith",
    "Speak good or remain silent. — Hadith",
    "Allah does not burden a soul beyond that it can bear. — Quran 2:286",
    "Be in this world as though you were a stranger or a traveller. — Hadith",
    "Cleanliness is half of faith. — Hadith",
]


class Islamic(commands.Cog):
    def __init__(self, bot):
        self.bot     = bot
        self.session = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    # ── /quran ────────────────────────────────────────────────
    @app_commands.command(name="quran",
                          description="Get a Quran verse")
    @app_commands.describe(
        surah="Surah number (1-114)",
        ayah="Ayah number",
    )
    async def quran(self, interaction: discord.Interaction,
                    surah: int, ayah: int):
        await interaction.response.defer()
        url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,en.asad"
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ Verse not found.")
                    return
                data  = await resp.json()
                edits = data["data"]
                arabic = edits[0]["text"]
                english = edits[1]["text"]
                ref     = edits[1]["surah"]["englishName"]

                embed = discord.Embed(
                    title=f"📖 {ref} — {surah}:{ayah}",
                    color=COLOR_RED,
                )
                embed.add_field(name="Arabic",  value=arabic,  inline=False)
                embed.add_field(name="English", value=english, inline=False)
                await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    # ── /pray (prayer times) ──────────────────────────────────
    @app_commands.command(name="pray",
                          description="Get today's prayer times")
    @app_commands.describe(city="Your city name", country="Country code e.g. GB")
    async def pray(self, interaction: discord.Interaction,
                   city: str, country: str = "US"):
        await interaction.response.defer()
        url = (
            f"https://api.aladhan.com/v1/timingsByCity"
            f"?city={city}&country={country}&method=2"
        )
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ City not found.")
                    return
                data   = (await resp.json())["data"]["timings"]
                embed  = discord.Embed(
                    title=f"🕌 Prayer Times — {city}",
                    color=COLOR_RED,
                )
                prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
                for p in prayers:
                    embed.add_field(name=p, value=data[p], inline=True)
                await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    # ── /dhikr ────────────────────────────────────────────────
    @app_commands.command(name="dhikr",
                          description="Get a dhikr to recite")
    async def dhikr(self, interaction: discord.Interaction):
        user = await get_user(interaction.user.id)
        count = user.get("dhikr_count", 0) + 1
        await update_user(interaction.user.id, {"dhikr_count": count})

        if count >= 100:
            await award_badge(interaction.user.id, "dhikr_king")

        embed = discord.Embed(
            title="📿 Dhikr",
            description=random.choice(DHIKR_LIST),
            color=COLOR_RED,
        )
        embed.set_footer(text=f"Your dhikr count: {count}")
        await interaction.response.send_message(embed=embed)

    # ── /quote ────────────────────────────────────────────────
    @app_commands.command(name="quote",
                          description="Get an Islamic/motivational quote")
    async def quote(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💬 Islamic Quote",
            description=random.choice(ISLAMIC_QUOTES),
            color=COLOR_RED,
        )
        await interaction.response.send_message(embed=embed)

    # ── /hadith ───────────────────────────────────────────────
    @app_commands.command(name="hadith",
                          description="Get a random hadith")
    async def hadith(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = "https://random-hadith-generator.vercel.app/bukhari/"
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send(
                        f"📿 {random.choice(ISLAMIC_QUOTES)}"
                    )
                    return
                data  = await resp.json()
                embed = discord.Embed(
                    title=f"📜 Hadith — {data.get('book', 'Bukhari')}",
                    description=data.get("hadith_english", "No text."),
                    color=COLOR_RED,
                )
                embed.set_footer(
                    text=f"Chapter: {data.get('chapterName', 'Unknown')}"
                )
                await interaction.followup.send(embed=embed)
        except Exception:
            await interaction.followup.send(
                f"📿 {random.choice(ISLAMIC_QUOTES)}"
            )


async def setup(bot):
    await bot.add_cog(Islamic(bot))