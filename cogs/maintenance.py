import discord
from discord.ext import commands
from logger import logger
import asyncio
import sys
import os
from utils import set_activity
from globals import DEFAULT_ACTIVITY, MAINTENANCE_ACTIVITY
class Maintenance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.mode = False

    @discord.app_commands.command(name="maintenance", description="Включение/выключение режима техобслуживания")
    @discord.app_commands.describe(mode="Выберите режим")
    @discord.app_commands.checks.has_role("Supreme Intelligence")
    async def maintenance(self, interaction: discord.Interaction, mode: bool):
        self.bot.mode = mode
        if self.bot.mode:
            status = "включен."
            await set_activity(self.bot, activity_text=MAINTENANCE_ACTIVITY, status=discord.Status.idle)
        else:
            status = "выключен."
            await set_activity(self.bot, activity_text=DEFAULT_ACTIVITY)
            
        await interaction.response.send_message(f"Режим техобслуживания {status}", ephemeral=True)

    @commands.hybrid_command(name="shutdown", description="Выключение бота")
    @commands.has_role("Supreme Intelligence")
    async def shutdown(self, ctx: commands.Context):
        await ctx.send("Выключение бота", ephemeral=True)
        await asyncio.sleep(10)
        await self.bot.close()


    @commands.hybrid_command(name="restart", description="Перезапуск бота")
    @commands.has_role("Supreme Intelligence")
    async def restart(self, ctx: commands.Context):
        python = sys.executable 
        msg = await ctx.send("Перезапуск систем... ", ephemeral=True)
        os.execv(python, [python] + sys.argv) 
        msg.edit (content="Бот перезапущен")

    COG_MODULES = [
        discord.app_commands.Choice(name="commands", value="commands"),
        discord.app_commands.Choice(name="events", value="events"),
        discord.app_commands.Choice(name="maintenance", value="maintenance"),
        discord.app_commands.Choice(name="games", value="games"),
        discord.app_commands.Choice(name="voice", value="voice"),
        discord.app_commands.Choice(name="soundboard", value="soundboard")

    ]

    @discord.app_commands.command(name="reload", description="Перезагружает системные компоненты бота")
    @discord.app_commands.choices(module=COG_MODULES)
    @discord.app_commands.describe(module="Выберите модуль")
    @discord.app_commands.checks.has_role("Supreme Intelligence")
    async def reload (self, interaction: discord.Interaction, module: str):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await self.bot.reload_extension(f'cogs.{module}')
            await interaction.followup.send(f"🧩 Модуль {module} успешно перезагружен.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ошибка при перезагрузке модуля {module}: {e}", ephemeral=True)
            logger.error(f"Ошибка при перезагрузке модуля {module}: {e}")

    @discord.app_commands.command(name="test", description="Команда тестирования")
    @discord.app_commands.checks.has_role("Supreme Intelligence")
    async def test (self, interaction: discord.Interaction):
       await interaction.response.send_message(content="Hello World", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        logger.info (f"Команда '{ctx.command}' вызвана пользователем {ctx.author}, канал: {ctx.channel}")
        if self.bot.mode and ctx.command.name != "maintenance":
            await ctx.send("🛠️Бот в режиме тех. обслуживания.🛠️", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.command:
            logger.info (f"Команда '{interaction.command.name}' вызвана пользователем {interaction.user.display_name}, канал: {interaction.channel}")
            if self.bot.mode and interaction.command and interaction.command.name != "maintenance":
                if not interaction.response.is_done(): 
                    await interaction.followup.send("🛠️Бот в режиме тех. обслуживания. Некоторые команды могут работать некорректно или не работать вовсе 🛠️", ephemeral=True)
        else:
            #уточнить логирование для панелей и модальных окон
            interaction_type = interaction.type.name if hasattr(interaction.type, 'name') else str(interaction.type)
            custom_id = interaction.data.get("custom_id") if interaction.data else None
            logger.info(f"[{interaction_type}] Взаимодействие без команды. Пользователь: {interaction.user.display_name}, custom_id: {custom_id}, канал: {interaction.channel}"
        )
async def setup(bot: commands.Bot):
   await bot.add_cog(Maintenance(bot)) 
   logger.info ("Модуль управления загружен.")
   
