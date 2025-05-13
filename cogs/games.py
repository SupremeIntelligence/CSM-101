import random
import discord
from discord.ext import commands
from logger import logger
import asyncio
import guild_info
import globals
from user import sort_list, get_list, User
import datetime

def _frmt(text: str, bar: str, width: int = 50, fillchar: str = " ") -> str:
            padded_text = text.ljust(width, fillchar)  
            return f"{padded_text}{bar}"
class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._start_daily_lottery_task()

    games = discord.app_commands.Group(name="games", description="Интерактивные игры")

    def _start_daily_lottery_task (self) -> None:
        task_name = "Daily-Lottery-Task"
        tasks = asyncio.all_tasks()
        for task in tasks:
            if task.get_name() == task_name:
                task.cancel()
        self.bot.loop.create_task(self.daily_lottery_task(), name=task_name)
        logger.info("#DAILY_LOTTERY_TASK: Task started.")

        """for task in tasks:
            if task.get_name() == task_name:
                task_started = True
        if not task_started:
            self.bot.loop.create_task(self.daily_lottery_task(), name=task_name)
            logger.info("#DAILY_LOTTERY_TASK: Task started.")
        else:
            logger.info("#DAILY_LOTTERY_TASK: Task is already running.")"""

    @staticmethod
    def get_winner (users: dict[int, User]) -> User:
        winner_id = random.choice(list(users.keys()))
        winner = globals.users[winner_id]
        winner.wins+=1
        guild_info.save_users(users)
        return winner
    
    @games.command(name="pidor", description="Определяет главного пидора сервера")
    async def playPid(self, interaction:discord.Interaction):

        embed = discord.Embed(title="🔍 Система поиска пидорасов",
                              description="Инициализация алгоритма поиска пидорасов...", 
                              color=discord.Color.red())
        
        await interaction.response.send_message(embed=embed)

        nb_space = "\u00A0"
        stages = [
        ("Инициализация алгоритма поиска пидорасов...", 1, discord.Color.red()),
        (_frmt(text="Установление связи с сервером Мерчера...", bar="▓▓▓░░░░░░░░ 20%", fillchar=nb_space), 2, discord.Color.orange()),
        (_frmt(text="Проверка системы безопасности...", bar=" ▓▓▓▓▓░░░░░░ 40%", fillchar=nb_space), 2, discord.Color(0xFFA500)),
        (_frmt(text="Взлом брандмауэра...", bar="▓▓▓▓▓▓▓░░░░ 75%", fillchar=nb_space), 2, discord.Color(0x9ACD32)),
        (_frmt(text="Доступ получен. Анализ базы данных...", bar="▓▓▓▓▓▓▓▓▓▓▓ 100%", fillchar=nb_space), 4, discord.Color.brand_green())
        ]
        for stage_text, delay, color in stages:
            embed.description = stage_text
            embed.color = color
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(delay)
        
        winner_stats = Games.get_winner(globals.users)

        winner = await interaction.guild.fetch_member(winner_stats.id)
        avatar_url = winner.avatar.url if winner.avatar else winner.default_avatar.url
        embed.title = "🎉 Результат анализа"
        embed.description = f"🏆 **Главный пидорас сервера:** <@{winner_stats.id}>"
        embed.color = discord.Color.green()
        embed.set_footer(text="Поздравляем победителя!")
        embed.set_thumbnail(url=avatar_url)

        await interaction.edit_original_response(embed=embed)

        logger.info(f"Пользователь {winner_stats.username} ({winner_stats.id}) побеждает в игре pidor")

    @games.command(name="user-stats", description="Личная статистика пользователя")
    @discord.app_commands.describe(user="Выберите пользователя, чью статистику хотите увидеть")
    async def user_stats(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        user_stats = globals.users.get(user.id)

        if user_stats is None:
            user_stats = User(id=user.id, username=user.display_name)
            
        embed = discord.Embed (
            title=f"📊 Статистика пользователя **{user_stats.username}**:",
            color = user.color
        )

        formatted_date = user.joined_at.strftime('%d.%m.%Y')
        embed.add_field (name="Сколько раз был пидорасом:", value=f" **{user_stats.wins}**", inline=True)
        embed.add_field(name="",value="", inline=True)
        embed.add_field (name="Дата вступления на сервер:", value=f" **{formatted_date}**", inline=True)

        await interaction.response.send_message(embed=embed)

    @games.command(name="server-stats",description="Список всех выявленных пидорасов на сервере:")
    async def server_stats(self, interaction:discord.Interaction):
        users_list = get_list(globals.users)
        sort_list(users_list)
        top_users = users_list[:10]

        embed = discord.Embed(
            title="🏆 Топ-10 пидорасов сервера:",
            color=discord.Color.gold()
    )
        lines = [f"{i+1}. **{user.username}**: **{user.wins}**" for i, user in enumerate(top_users)]
        embed.add_field(name="", value="\n".join(lines), inline=False)
        await interaction.response.send_message(embed=embed)

    @staticmethod
    async def play (channel: discord.TextChannel, count: int = 3):
        embed = discord.Embed(title="🔍 Система поиска пидорасов",
                        description="Инициализация алгоритма поиска пидорасов...", 
                        color=discord.Color.red())
        
        message =  await channel.send (embed=embed)

        nb_space = "\u00A0"
        stages = [
        ("Инициализация алгоритма поиска пидорасов...", 1, discord.Color.red()),
        (_frmt(text="Захват сигнала из локальной сети **Mercher**...", bar="▓▓▓░░░░░░░░ 20%", fillchar=nb_space, width=53), 2, discord.Color.orange()),
        (_frmt(text="Проверка системы безопасности...", bar=" ▓▓▓▓▓░░░░░░ 40%", fillchar=nb_space, width=53), 2, discord.Color(0xFFA500)),
        (_frmt(text="Протокол взлома активен. Сопротивление бесполезно...", bar="▓▓▓▓▓▓▓░░░░ 75%", fillchar=nb_space, width=53), 2, discord.Color(0x9ACD32)),
        (_frmt(text="Доступ к ядру системы **Mercher** получен. Анализ...", bar="▓▓▓▓▓▓▓▓▓▓▓ 100%", fillchar=nb_space, width=53), 4, discord.Color.brand_green())
        ]
        for stage_text, delay, color in stages:
            embed.description = stage_text
            embed.color = color
            message = await message.edit(embed=embed)
            await asyncio.sleep(delay)
    
        winners = [Games.get_winner(globals.users) for _ in range(count)]
        medals = ("🥇","🥈","🥉")

        embed.description = "🏆 **Топ-3 пидораса дня:**"
        embed.color = discord.Color.green()

        embeds = []
        embeds.append(embed)
        guild = message.guild
        for i, winner_stats in enumerate(winners):
            winner_embed = discord.Embed (
                    title=f"{medals[i]}Пидор #{i+1}",
                    description=f"<@{winner_stats.id}>",
                    color=discord.Color.green()
                    )
            
            winner = await guild.fetch_member(winner_stats.id)
            avatar_url = winner.avatar.url if winner.avatar else winner.default_avatar.url
            winner_embed.set_thumbnail(url=avatar_url)
            embeds.append(winner_embed)
            logger.info(f"#AUTO_TASK: Победитель #{i+1} — {winner_stats.username} ({winner_stats.id}) в игре pidor")

            """embed.add_field(name=f"{medals[i]} Пидор #{i+1}",
                             value=f"<@{winner_stats.id}>",
                             inline=True)"""
            
        await message.edit (embeds=embeds)

    async def daily_lottery_task(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed(): 
            now = datetime.datetime.now()
            target_time = now.replace (hour=20, minute=00, second=0, microsecond=0)
            if now > target_time:
                target_time += datetime.timedelta(days=1)
            wait_seconds = (target_time - now).total_seconds()
            wait_mins = wait_seconds/60
            logger.debug(f"#DAILY_LOTTERY_TASK: {wait_mins:.1f}min is left")
            await asyncio.sleep (wait_seconds)

            channel = self.bot.get_channel(globals.LAMP_CHANNEL_ID)
            await channel.send ("Пришло время для правосудия.")
            await Games.play(channel)
            logger.info ("#DAILY_LOTTERY_TASK: Task completed.")
            await asyncio.sleep (60)

async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
    logger.info ("Игровой модуль загружен.")



    