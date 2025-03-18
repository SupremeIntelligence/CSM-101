import random
import discord
from discord.ext import commands
from logger import logger
import asyncio
import guild_info
import globals
from user import sort_list, get_list
class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    games = discord.app_commands.Group(name="games", description="Интерактивные игры")

    @games.command(name="pidor", description="Определяет главного пидора сервера")
    async def playPid(self, interaction:discord.Interaction):
        await interaction.response.send_message("Инициализация алгоритма поиска пидорасов....")
        winner_id = random.choice(list(globals.users.keys()))
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
        await interaction.edit_original_response(content=f"<@{globals.users[winner_id].id}> - главный пидорас сервера.")
        globals.users[winner_id].wins += 1
        guild_info.save_users(globals.users)
        logger.info(f"Игрок {globals.users[winner_id].username} ({globals.users[winner_id].id}) побеждает в игре pidor")

    @games.command(name="user-stats", description="Личная статистика")
    async def user_stats(self, interaction: discord.Interaction):
        user = globals.users[interaction.user.id]
        message = f'''
Пользователь: **{user.username}**
Сколько раз был пидорасом: **{user.wins}**
'''
        await interaction.response.send_message(message)

    @games.command(name="server-stats",description="Список всех выявленных пидорасов на сервере:")
    async def server_stats(self, interaction:discord.Interaction):
        users_list = get_list(globals.users)
        sort_list(users_list)
        top_users = users_list[:10]
        message = "Список пидорасов:\n" + "\n".join(f"{i+1}. **{user.username}**: **{user.wins}**" for i, user in enumerate(top_users))
        await interaction.response.send_message(message)

async def setup(bot):
    await bot.add_cog(Games(bot))