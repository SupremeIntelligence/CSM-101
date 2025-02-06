import random
import discord
from discord.ext import commands
from pid import get_channel_members
from logger import logger
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    games = discord.app_commands.Group(name="games", description="Интерактивные игры")

    @games.command(name="pidor", description="Определяет главного пидора сервера")
    async def playPid(self, interaction:discord.Interaction):
        await interaction.response.send_message("Инициализация алгоритма поиска пидорасов....")
        players = get_channel_members(interaction.guild, interaction.channel)
        winner_index = random.randint(0, len(players) - 1) 
        winner = players[winner_index]
        await asyncio.sleep(2)
        await interaction.edit_original_response(content="Установление связи с сервером Мерчера...")
        await asyncio.sleep(2)
        await interaction.edit_original_response(content="Проверка системы безопасности...  ▓▓▓▓▓░░░░░░ 40%")
        await asyncio.sleep(2)
        await interaction.edit_original_response(content="Декодирование протокола связи...  ▓▓▓▓▓▓░░░░░ 52%")
        await asyncio.sleep(2)
        await interaction.edit_original_response(content="Взлом брандмауэра... ▓▓▓▓▓▓▓░░░ 75%")
        await asyncio.sleep(2)
        await interaction.edit_original_response(content="Доступ получен. Анализ базы данных... ▓▓▓▓▓▓▓▓▓▓▓▓ 100%")
        await asyncio.sleep(4)
        await interaction.edit_original_response(content=f"<@{winner.id}> - главный пидорас сервера.")
        logger.info(f"Игрок {winner.display_name} ({winner.id}) побеждает в игре pidor")

    #@games.command(name="pidor stats", description="Список всех выявленных на сервере пидорасов")
    #async def statsPid(self, interaction: discord.Interaction):
    #    pass
    
async def setup(bot):
    await bot.add_cog(Games(bot))