import discord
from discord.ext import commands
from logger import logger
import guild_info
import globals
import random
from typing import Optional
import asyncio

async def send_announcement(bot: commands.Bot, announcement_channel_id: int, message: str = None, embed: discord.Embed = None):
    channel = bot.get_channel(announcement_channel_id)
    if channel:
        if message:
            await channel.send(content=message)
            logger.info (f"Объявление опубликовано в канале {channel.name}.")
        elif embed:
            await channel.send(embed=embed)
            logger.info (f"Объявление '{embed.title}' опубликовано в канале {channel.name}.")
    else:
        logger.warning(f"Канал с ID {announcement_channel_id} не найден.")

async def set_activity(bot: commands.Bot,
                       activity_text: str = None,
                       activity_type: Optional[discord.ActivityType] = None,
                       status: discord.Status = discord.Status.online):
    if activity_text is None:
        await bot.change_presence(status=status, activity=None)
        return

    if activity_type is None:
        activity = discord.CustomActivity(name=activity_text)
    else:
        activity = discord.Activity(name=activity_text, type=activity_type)

    await bot.change_presence(status=status, activity=activity)

async def load_cogs(bot:commands.Bot):
    reload = False
    for module in globals.COG_MODULES:
        extension = f'cogs.{module}'
        if extension in bot.extensions:
            await bot.reload_extension(extension)
            reload = True
        else:
            await bot.load_extension(extension)
    if reload:
        logger.info("Все командные модули перезагружены") 
    else:
        logger.info("Все командные модули загружены") 
    

def sync_stats (bot: commands.Bot):
    globals.users = guild_info.load_users(filename=globals.USER_DATA_FILE)
    logger.info("Данные users.json загружены")
    guild_info.sync_users(bot, globals.SERVER_ID, globals.LAMP_CHANNEL_ID, globals.users)
    logger.info("Данные users.json синхронизированы с данными Discord")

def load_jokes(filename = globals.JOKES_DATA_FILE):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
    
            return content.split("\n///...///\n")
            
    except FileNotFoundError:
        logger.critical("Файл анекдотов не найден.")
    except Exception as e:
        logger.critical(f"Ошибка при получении анекдота: {e}")

def get_joke(jokes: list[str]):
    return random.choice(jokes)

def print_all_tasks ():
    tasks = asyncio.all_tasks()  # Можно передать loop, если нужно
    print(f"🔍 Найдено {len(tasks)} задач:")
    for task in tasks:
        print(f"- {task.get_name()} | {task}")

async def clear_commands (bot: commands.Bot):
    await bot.tree.sync()
    bot.tree.clear_commands(guild=None)