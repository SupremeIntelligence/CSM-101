import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from logger import logger
from joke import load_jokes
import guild_info
import globals

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

@bot.tree.command(name="test",description="test slash command")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message("Hello World!", ephemeral=True)
    
async def load_cogs():
    for module in globals.COG_MODULES:
        await bot.load_extension (f'cogs.{module}')
    logger.info("Все командные модули загружены")

async def set_activity():
    #server_emoji = discord.PartialEmoji(name="Witcher_Triss", id=856435197709123645)
    custom_activity = discord.CustomActivity(name="Следит за Мерчером 👀")
    await bot.change_presence(activity=custom_activity)

def sync_stats ():
    globals.users = guild_info.load_users(filename=globals.USER_DATA_FILE)
    logger.info("Данные users.json загружены")
    guild_info.sync_users(bot, globals.SERVER_ID, globals.LAMP_CHANNEL_ID, globals.users)
    logger.info("Данные users.json синхронизированы с данными Discord")

@bot.event
async def on_ready():
    sync_stats()
    await load_cogs()
    await bot.tree.sync()
    await set_activity()
    globals.jokes = load_jokes()
    logger.info("База анекдотов загружена")
    sys_channel_id = globals.SYS_CHANNEL_ID
    sys_channel = bot.get_channel(sys_channel_id)
    if sys_channel:
        await sys_channel.send("Бот запущен")
    for guild in bot.guilds:
        logger.info(f"Бот {bot.user} работает на сервере: {guild.name} (ID: {guild.id})")

load_dotenv("config.env")
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN) 
