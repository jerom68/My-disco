import os
import discord
import random
import aiohttp
import asyncio
from discord.ext import commands, tasks
from flask import Flask

# Flask app for Render port binding
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# Discord bot setup
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Set this in Render environment variables
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Auto Slowmode (applies to every channel)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                await channel.edit(slowmode_delay=5)  # 5 seconds slowmode
            except discord.Forbidden:
                print(f"Missing permissions for {channel.name}")

# DM new members with avatar image
@bot.event
async def on_member_join(member):
    try:
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed = discord.Embed(title="Welcome!", description=f"Hello {member.mention}, welcome to the server!", color=discord.Color.blue())
        embed.set_image(url=avatar_url)
        await member.send(embed=embed)
    except discord.HTTPException:
        print(f"Could not DM {member}")

# Fun game (Rock-Paper-Scissors)
@bot.command()
async def rps(ctx, choice: str):
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    result = f"You chose {choice}, I chose {bot_choice}."

    if choice == bot_choice:
        result += " It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result += " You win!"
    else:
        result += " I win!"

    await ctx.send(result)

# Pokémon info command
@bot.command()
async def pokemon(ctx, name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(title=name.capitalize(), color=discord.Color.red())
                embed.set_image(url=data["sprites"]["front_default"])
                embed.add_field(name="Type", value=", ".join(t["type"]["name"] for t in data["types"]))
                await ctx.send(embed=embed)
            else:
                await ctx.send("Pokémon not found!")

# Anime quotes
@bot.command()
async def animequote(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://animechan.xyz/api/random") as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(f'"{data["quote"]}" - {data["character"]} ({data["anime"]})')

# Anime search
@bot.command()
async def anime(ctx, *, query: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.jikan.moe/v4/anime?q={query}") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["data"]:
                    anime = data["data"][0]
                    embed = discord.Embed(title=anime["title"], url=anime["url"], description=anime["synopsis"], color=discord.Color.green())
                    embed.set_image(url=anime["images"]["jpg"]["image_url"])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Anime not found!")
            else:
                await ctx.send("Error fetching anime data!")

# Character info by name
@bot.command()
async def character(ctx, *, name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.jikan.moe/v4/characters?q={name}") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["data"]:
                    char = data["data"][0]
                    embed = discord.Embed(title=char["name"], url=char["url"], color=discord.Color.purple())
                    embed.set_image(url=char["images"]["jpg"]["image_url"])
                    embed.add_field(name="About", value=char["about"][:500] + "...", inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Character not found!")
            else:
                await ctx.send("Error fetching character data!")

# Meme generation
@bot.command()
async def meme(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(title=data["title"], url=data["postLink"], color=discord.Color.orange())
                embed.set_image(url=data["url"])
                await ctx.send(embed=embed)
            else:
                await ctx.send("Error fetching meme!")

# Anime news posting (Crunchyroll)
@tasks.loop(hours=6)  # Adjust interval as needed
async def post_anime_news():
    channel_id = int(os.getenv("ANIME_NEWS_CHANNEL_ID"))  # Set this in Render environment variables
    channel = bot.get_channel(channel_id)
    if not channel:
        print("Anime news channel not found!")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.crunchyroll.com/news/rss") as resp:
            if resp.status == 200:
                from xml.etree import ElementTree as ET
                xml = await resp.text()
                root = ET.fromstring(xml)
                latest_news = root.findall(".//item")[0]
                title = latest_news.find("title").text
                link = latest_news.find("link").text
                await channel.send(f"**{title}**\n{link}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    post_anime_news.start()  # Start the anime news loop

# Run Flask app and bot
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))).start()
    bot.run(TOKEN)
