import discord
from discord.ext import commands
import asyncio
import globals
from joke import get_joke
from logger import logger

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Вызов бота")
    async def ping(self, interaction: discord.Integration):
        
        message = await interaction.response.send_message("Скажи да")

        def check(m: discord.Message):
            return m.author == interaction.user and m.channel == interaction.channel
        try:
            response = await self.bot.wait_for("message", timeout=20.0, check=check)
            if response.content.lower() == "да":
                await interaction.edit_original_response(content="Сосал?")
            elif response.content.lower() == "нет":
                await response.reply("пидора ответ")
            elif response.content.lower() == "пизда":
                await response.reply("хуй на")
            else:
                await response.reply("ок")
        except asyncio.TimeoutError:
            await interaction.followup.send("Игнорщик ебаный")

    @discord.app_commands.command(name="dinamo", description="Любимый клуб Мерчера")
    async def dinamo(self, interaction: discord.Interaction):
        await interaction.response.send_message("ДИНАМО")

    @discord.app_commands.command(name="call-mercher", description="Say his name")
    async def call_mercher(self, interaction: discord.Interaction):
        message = f"""<@{globals.MERCHER_ID}>, как дела?```diff
+ ░▒█▀▄▀█░▒█▀▀▀░▒█▀▀▄░▒█▀▀▄░▒█░▒█░▒█▀▀▀░▒█▀▀▄
- ░▒█▒█▒█░▒█▀▀▀░▒█▄▄▀░▒█░░░░▒█▀▀█░▒█▀▀▀░▒█▄▄▀
+ ░▒█░░▒█░▒█▄▄▄░▒█░▒█░▒█▄▄▀░▒█░▒█░▒█▄▄▄░▒█░▒█
```"""
        await interaction.response.send_message(message)

    @discord.app_commands.command(name="joke", description="Анекдот от Мерчер бота")
    async def joke(self, interaction:discord.Interaction):
        joke = get_joke(globals.jokes)
        message = f"```{joke}```"
        await interaction.response.send_message(message)

    @discord.app_commands.command (name="walk", description="Отправляет погулять выбранного пользователя")
    @discord.app_commands.describe(user="Выберите цель:", duration="Определите время пытки")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def walk (self, interaction: discord.Interaction, user: discord.Member, duration: int = 15):
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message(f"{user.mention} не находится в голосовом канале!", ephemeral=True)
            return
        if user.id == globals.SUPREME_INTELLIGENCE_ID and interaction.user.id != globals.SUPREME_INTELLIGENCE_ID:
            await interaction.response.send_message ("Ты че, охуел?")
            user = interaction.user
            await interaction.followup.send("Инициализация боевого протокола....")  
        else:
            await interaction.response.send_message("Инициализация боевого протокола....")

        await asyncio.sleep(1)
        original_channel = user.voice.channel
        voice_channels = [ch for ch in interaction.guild.voice_channels]
        end_time = discord.utils.utcnow().timestamp() + duration

        index = 0
        delay = 0.1
        while discord.utils.utcnow().timestamp() < end_time:
            new_channel = voice_channels[index % len(voice_channels)]
            await user.move_to(new_channel)
            await asyncio.sleep(delay)  
            delay -= 0.005
            index += 1
        await user.move_to(original_channel)
        await interaction.edit_original_response(content = f"Пользователь {user.mention} гулял в течение {duration} секунд.")

async def setup(bot):
   await bot.add_cog(Commands(bot)) 
   logger.info ("Основной командный модуль загружен.")
   

   
# class TrollControlView(discord.ui.View):
#     def __init__(self, cog: Commands, member: discord.Member, voice_channels):
#         super().__init__()
#         self.cog = cog
#         self.member = member
#         self.voice_channels = voice_channels
#         self.running = False

#     @discord.ui.button(label="Старт", style=discord.ButtonStyle.green)
#     async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.running:
#             await interaction.response.send_message("⚠ Перемещение уже запущено!", ephemeral=True)
#             return
        
#         self.running = True
#         index = 0
#         self.cog.active_trolls[self.member.id] = True

#         while self.running and self.cog.active_trolls.get(self.member.id, False):
#             new_channel = self.voice_channels[index % len(self.voice_channels)]
#             await self.member.move_to(new_channel)
#             await asyncio.sleep(2)  # Задержка перед следующим перемещением
#             index += 1

#     @discord.ui.button(label="Стоп", style=discord.ButtonStyle.red)
#     async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.running = False
#         self.cog.active_trolls[self.member.id] = False
#         await self.member.move_to(None)  # Выкидываем из голосового канала в конце
#         await interaction.response.send_message(f"✅ {self.member.mention} больше не страдает. 😈")
#         self.stop()