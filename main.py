import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from logger import logger
from pid import get_channel_members

#Mercher ID = 496954299243560960
#Ламповая Флудилка ID = 695673593618497678

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

@bot.tree.command(name="test",description="test slash command")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message("Hello World!", ephemeral=True)
    
async def load_cogs():
    cogs = ["cogs.commands", "cogs.events", "cogs.maintenance", "cogs.games"]
    for cog in cogs:
        await bot.load_extension(cog)
    logger.debug("Cogs loaded.")

async def set_activity():
    #server_emoji = discord.PartialEmoji(name="Witcher_Triss", id=856435197709123645)
    custom_activity = discord.CustomActivity(name="Следит за Мерчером 👀")
    await bot.change_presence(activity=custom_activity)

@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()
    await set_activity()
    sys_channel_id = 1002897000573960202
    channel_id = 695673593618497678
    channel = bot.get_channel(channel_id)
    sys_channel = bot.get_channel(sys_channel_id)
    if channel:
        pass
        #await channel.send("<@496954299243560960>, как дела?")
        await sys_channel.send("Бот запущен")
    
    for guild in bot.guilds:
        logger.info(f"Бот {bot.user} работает на сервере: {guild.name} (ID: {guild.id})")

load_dotenv("config.env")
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN) 
