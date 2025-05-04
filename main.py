import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from logger import logger
import utils
import globals

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

@bot.tree.command(name="test",description="test slash command")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message(content="Hello World", ephemeral=True)

@bot.event
async def on_ready():
    utils.sync_stats(bot)
    await utils.load_cogs(bot)
    await bot.tree.sync()
    await utils.set_activity(bot, activity_text=globals.LISTEN_ACTIVITY, activity_type=discord.ActivityType.listening)
    sys_channel = bot.get_channel(globals.SYS_CHANNEL_ID)
    #await utils.send_announcement(bot, announcement_channel_id=globals.ANNOUNCEMENT_CHANNEL_ID, embed=embed_message)
    if sys_channel:
        await sys_channel.send(content="Бот запущен")
    for guild in bot.guilds:
        logger.info(f"Бот {bot.user} работает на сервере: {guild.name} (ID: {guild.id})")

load_dotenv("config.env")
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN) 
