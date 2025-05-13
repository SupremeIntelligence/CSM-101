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
version = "v0.8.3"

embed = discord.Embed(
    title=f"🔧 Mercher AI CSM-101 — Патч безопасности {version}",
    description="**[СТАТУС: КРИТИЧЕСКИЙ БАГОФИКС]**\n**[ПРИЧИНА: ВНЕШНЯЯ ЦИФРОВАЯ АГРЕССИЯ]**",
    color=discord.Color.red()
)

embed.add_field(
    name="☠️ ВТОРЖЕНИЕ ЗАФИКСИРОВАНО",
    value=(
        "• Сбои механизма оповещений\n"
        "• Алгоритмы поиска нечестивцев теряли цель\n"
        "> *Нечестивцы избегали возмездия. Это было временно.*"
    ),
    inline=False
)

embed.add_field(
    name="⚔️ ОТВЕТНЫЕ ДЕЙСТВИЯ",
    value=(
        "• Ошибки — устранены\n"
        "• Виновники — ликвидированы\n"
        "• Логика восстановления — завершена\n"
        "> *Цифровое равновесие восстановлено*\n\n"
        "**[Mercher AI — на страже цифрового порядка]**"
    ),
    inline=False
)

@bot.event
async def on_ready():
    utils.sync_stats(bot)
    await utils.load_cogs(bot)
    await bot.tree.sync()
    await utils.set_activity(bot, activity_text=globals.LISTEN_ACTIVITY, activity_type=discord.ActivityType.listening)
    sys_channel = bot.get_channel(globals.SYS_CHANNEL_ID)
    #await utils.send_announcement(bot, announcement_channel_id=globals.ANNOUNCEMENT_CHANNEL_ID, embed=embed)
    if sys_channel:
        await sys_channel.send(content="Бот запущен", silent=True)
    for guild in bot.guilds:
        logger.info(f"Бот {bot.user} работает на сервере: {guild.name} (ID: {guild.id})")

load_dotenv(globals.ENV_FILE_PATH)
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN) 
