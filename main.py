import discord
import requests
import random
import asyncio
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import os

# Bot setup
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Feature 1: Auto Slowmode for Every Channel ---
@bot.event
async def on_message(message):
    if not message.author.bot:  # Avoid bot messages triggering slowmode
        await message.channel.edit(slowmode_delay=5)  # 5-second slowmode
    await bot.process_commands(message)

# --- Feature 2: DM Members on Join with Avatar ---
@bot.event
async def on_member_join(member):
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    embed = discord.Embed(title="Welcome!", description=f"Hi {member.name}, welcome to the server!", color=0x00ff00)
    embed.set_thumbnail(url=avatar_url)
    await member.send(embed=embed)

# --- Feature 3: Fun Games (Dice Roll) ---
@bot.command()
async def roll(ctx):
    number = random.randint(1, 6)
    await ctx.send(f"🎲 You rolled a {number}!")

# --- Feature 4: Pokémon Info ---
@bot.command()
async def pokemon(ctx, name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        embed = discord.Embed(title=data["name"].capitalize(), color=0xff0000)
        embed.set_thumbnail(url=data["sprites"]["front_default"])
        embed.add_field(name="ID", value=data["id"], inline=True)
        embed.add_field(name="Height", value=data["height"], inline=True)
        embed.add_field(name="Weight", value=data["weight"], inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Pokémon not found!")

# --- Feature 5: Anime Quotes ---
@bot.command()
async def quote(ctx):
    quotes = [
        "Power comes in response to a need, not a desire. – Goku",
        "Fear is not evil. It tells you what your weaknesses are. – Gildarts Clive",
        "A person grows up when he has to. – Jiraiya"
    ]
    await ctx.send(random.choice(quotes))

# --- Feature 6: Anime Search ---
@bot.command()
async def anime(ctx, *, query: str):
    url = f"https://myanimelist.net/search/all?q={query}"
    await ctx.send(f"🔎 Search results for **{query}**: {url}")

# --- Feature 7: Character Info ---
@bot.command()
async def character(ctx, *, name: str):
    await ctx.send(f"🔎 Searching for character **{name}**...\nhttps://myanimelist.net/search/all?q={name}")

# --- Feature 8: Meme Generation ---
@bot.command()
async def meme(ctx):
    url = "https://meme-api.com/gimme"
    response = requests.get(url).json()
    embed = discord.Embed(title="Random Meme", color=0x3498db)
    embed.set_image(url=response["url"])
    await ctx.send(embed=embed)

# --- Feature 9: Fetch Anime News (Command) ---
@bot.command()
async def news(ctx):
    news_data = fetch_anime_news()
    if news_data:
        embed = discord.Embed(title="Latest Anime News", color=0xff5733)
        for title, link in news_data:
            embed.add_field(name=title, value=f"[Read more]({link})", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("No news found!")

# --- Fetch Anime News Helper Function ---
def fetch_anime_news():
    url = "https://www.crunchyroll.com/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", class_="news-link", limit=3)
    
    if articles:
        return [(article.text.strip(), f"https://www.crunchyroll.com{article['href']}") for article in articles]
    return []

# --- Feature 10: Automatically Post Anime News ---
@tasks.loop(hours=3)  # Runs every 3 hours
async def post_anime_news():
    channel_id = int(os.getenv("NEWS_CHANNEL_ID"))  # Securely fetch from Render
    channel = bot.get_channel(channel_id)
    
    if channel:
        news_data = fetch_anime_news()
        if news_data:
            embed = discord.Embed(title="Latest Anime News", color=0xff5733)
            for title, link in news_data:
                embed.add_field(name=title, value=f"[Read more]({link})", inline=False)
            await channel.send(embed=embed)

# Start the task when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    post_anime_news.start()

# --- Bot Token ---
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
