import discord
from discord.ext import commands
import aiohttp
import random
import time
import os
from flask import Flask
import threading

# Flask Web Server for Status Page
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.getenv("PORT", 8080))  # Default to 8080 if PORT is not set
    app.run(host="0.0.0.0", port=port)

thread = threading.Thread(target=run_web)
thread.start()

# ✅ Enable Required Intents
intents = discord.Intents.default()
intents.message_content = True  # Fix for commands not working
intents.members = True  # Needed for user info and welcome messages

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# 🏓 Ping Command
@bot.command()
async def ping(ctx):
    start_time = time.time()
    message = await ctx.send("Pinging...")
    end_time = time.time()
    latency = round(bot.latency * 1000)
    response_time = round((end_time - start_time) * 1000)
    await message.edit(content=f"🏓 Pong! Latency: {latency}ms | Response Time: {response_time}ms")

# 🎱 8Ball Command
@bot.command()
async def eightball(ctx, *, question):
    responses = ["Yes!", "No.", "Maybe...", "Definitely!", "Not sure.", "Ask again later."]
    await ctx.send(f"🎱 {random.choice(responses)}")

# 😂 Joke Command
@bot.command()
async def joke(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
            if resp.status == 200:
                joke_data = await resp.json()
                await ctx.send(f"{joke_data['setup']} - {joke_data['punchline']}")
            else:
                await ctx.send("Couldn't fetch a joke at the moment!")

# 🤯 Fun Fact Command
@bot.command()
async def fact(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
            if resp.status == 200:
                fact_data = await resp.json()
                await ctx.send(f"💡 Fun Fact: {fact_data['text']}")
            else:
                await ctx.send("Couldn't fetch a fun fact at the moment!")

# 📚 Manga Search Command
@bot.command()
async def manga(ctx, *, name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.jikan.moe/v4/manga?q={name}") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["data"]:
                    manga_info = data["data"][0]
                    embed = discord.Embed(title=manga_info["title"], url=manga_info["url"], color=discord.Color.blue())
                    embed.add_field(name="📖 Synopsis", value=manga_info["synopsis"][:500] + "...", inline=False)
                    embed.set_image(url=manga_info["images"]["jpg"]["image_url"])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No manga found with that name!")
            else:
                await ctx.send("Couldn't fetch manga details at the moment.")

# 🎴 Anime Image Commands
@bot.command()
async def waifu(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.waifu.pics/sfw/waifu") as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(data["url"])

@bot.command()
async def husbando(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.waifu.pics/sfw/husbando") as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(data["url"])

@bot.command()
async def neko(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.waifu.pics/sfw/neko") as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(data["url"])

# 🖼 Avatar Command
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

# 🌐 Server Info Command
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.gold())
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="📂 Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="🔰 Roles", value=len(guild.roles), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

# 🆔 User Info Command
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member.name}", color=discord.Color.green())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="👤 Username", value=member.name, inline=True)
    embed.add_field(name="🏷️ ID", value=member.id, inline=True)
    embed.add_field(name="📅 Joined At", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="🎭 Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=False)
    await ctx.send(embed=embed)

# 🎭 Auto Slowmode Feature
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if len(message.content) > 200:
        try:
            await message.channel.edit(slowmode_delay=5)
            await message.channel.send("⚠️ Slowmode enabled due to spam!")
        except discord.Forbidden:
            print("I don't have permission to edit slowmode!")

    await bot.process_commands(message)  # ✅ Fix to ensure commands work

# 🎉 DM New Members on Join
@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="Welcome!", description=f"Hello {member.name}, welcome to **{member.guild.name}**! 🎉", color=discord.Color.blue())
    embed.set_image(url=member.avatar.url)
    try:
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Could not DM {member.name}.")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
