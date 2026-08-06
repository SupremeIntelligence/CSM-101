import discord
from discord.ext import commands
from logger import logger
import guild_info
import globals
import random
from typing import Optional
import asyncio
import json

async def send_announcement(bot: commands.Bot,
                            announcement_channel_id: int,
                            message: str = None,
                            embed: discord.Embed = None,
                            file: discord.File = None) -> None:
    channel = bot.get_channel(announcement_channel_id)
    if channel:
        if message:
            await channel.send(content=message)
            logger.info (f"Объявление опубликовано в канале {channel.name}.")
        elif embed:
            await channel.send(embed=embed, file=file)
            logger.info (f"Объявление '{embed.title}' опубликовано в канале {channel.name}.")
        elif file:
            await channel.send(file=file)
            logger.info (f"Файл опубликован в канале {channel.name}.")
    else:
        logger.warning(f"Канал с ID {announcement_channel_id} не найден.")

async def set_activity(bot: commands.Bot,
                       activity_text: str = None,
                       activity_type: Optional[discord.ActivityType] = None,
                       status: discord.Status = discord.Status.online) -> None:
    if activity_text is None:
        await bot.change_presence(status=status, activity=None)
        return

    if activity_type is None:
        activity = discord.CustomActivity(name=activity_text)
    else:
        activity = discord.Activity(name=activity_text, type=activity_type)

    await bot.change_presence(status=status, activity=activity)

async def load_cogs(bot:commands.Bot) -> None:
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
    

def sync_stats (bot: commands.Bot) -> None:
    globals.users = guild_info.load_users(filename=globals.USER_DATA_FILE)
    logger.info("Данные users.json загружены")
    guild_info.sync_users(bot, globals.SERVER_ID, globals.LAMP_CHANNEL_ID, globals.users)
    logger.info("Данные users.json синхронизированы с данными Discord")

def load_jokes(filename = globals.JOKES_DATA_FILE)  -> list[str]:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
    
            return content.split("\n///...///\n")
    except FileNotFoundError:
        logger.critical("Файл памяти не найден. ")
        return []
    except FileNotFoundError:
        logger.critical("Файл анекдотов не найден.")
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении анекдота: {e}")
        return []

def get_joke(jokes: list[str]) -> str:
    return random.choice(jokes)

def print_all_tasks () -> None:
    tasks = asyncio.all_tasks()  # Можно передать loop, если нужно
    print(f"🔍 Найдено {len(tasks)} задач:")
    for task in tasks:
        print(f"- {task.get_name()} | {task}")

async def clear_commands (bot: commands.Bot) -> None:
    await bot.tree.sync()
    bot.tree.clear_commands(guild=None)

def load_memory(filename=globals.MEMORY_FILE) -> list[dict[str, str]]:
    try:
        with open (filename, "r", encoding="utf-8") as file:
            memory = json.load(file)
            return memory
    except FileNotFoundError:
        logger.critical("Файл памяти не найден. ")
        return []
    except json.JSONDecodeError:
        logger.critical("Ошибка декодирования JSON в файле памяти.")
        return []
    except Exception as e:
        logger.error(f"Неизвестная ошибка при загрузке файла памяти: {e}")
        return []
    
def load_help_commands(filename=globals.HELP_COMMANDS_FILE) -> list[dict[str, str]]:
    try:
        with open (filename, "r", encoding="utf-8") as file:
            help_commands = json.load(file)
            return help_commands
    except FileNotFoundError:
        logger.critical("Файл со списком команд не найден.")
        return []
    except json.JSONDecodeError:
        logger.critical("Ошибка декодирования JSON в файле со списком команд.")
        return []
    except Exception as e:
        logger.error(f"Неизвестная ошибка при загрузке файла со списком команд: {e}")
        return []

def save_memory(memory:list[dict[str, str]], filename=globals.MEMORY_FILE) -> None:
    try:
        with open (filename, "w", encoding="utf-8") as file:
            json.dump(memory, file, ensure_ascii=False, indent=2)
            logger.info("Файл памяти успешно сохранен.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при сохранении файла памяти: {e}")