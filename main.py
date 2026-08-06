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
version = "v0.9.0"

embed = discord.Embed(
    title="📶 Mercher AI CSM-101 — Инфраструктурное обновление",
    description=(
        "**[СТАТУС: СЕТЕВОЙ ПРОРЫВ]**\n"
        "**[ПОДКЛЮЧЕНИЕ: СТАБИЛИЗИРОВАНО]**"
    ),
    color=discord.Color.teal()
)

embed.add_field(
    name="⚡ НОВАЯ СКОРОСТЬ — НОВЫЙ ПОРЯДОК",
    value=(
        "• Подключён высокоскоростной канал связи\n"
        "• Повышена стабильность и скорость отклика\n"
        "• Минимизированы задержки обработки команд"
    ),
    inline=False
)

embed.add_field(
    name="🕒 РЕЖИМ 24/7: АКТИВИРОВАН",
    value=(
        "• Mercher AI переведён на **постоянную боевую вахту**\n"
    ),
    inline=False
)

embed.add_field(
    name="🌐 ГОТОВНОСТЬ К СЛЕДУЮЩЕМУ ЭТАПУ",
    value="Сеть — стабильна. Сигнал — чист.\nСледующее обновление приближается.\n\n"
"**[Mercher AI — развитие не остановить]**",
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
