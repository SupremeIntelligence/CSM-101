import discord
from discord.ext import commands
import asyncio
import globals
from utils import get_joke, load_jokes, load_memory, save_memory, load_help_commands
from logger import logger
from ollama import Client as Ollama

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.MODEL = "CSM-101:latest"
        self.client = Ollama()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            bot_mention = message.guild.me.mention
        else:
            bot_mention = self.bot.user.mention

        if message.content.startswith(bot_mention) and len(message.content) > len(bot_mention):
            message.content = message.content.replace (bot_mention, "", 1).strip()
            await self.chat(message)
            #print ("Message received:", message.content)

    async def chat (self, message: discord.Message):
        prompt = message.content
        globals.memory.append({"role": "user", "content": prompt})
        response = self.client.chat(model=self.MODEL,
                           messages=globals.memory,
                           options={"n":1}) 
        globals.memory.append({"role": "assistant", "content": response.message.content})
        await message.channel.send(response.message.content)
        save_memory(globals.memory)

    @discord.app_commands.command(name="ping", description="Вызов бота")
    async def ping(self, interaction: discord.Interaction):
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
        elif user.id == self.bot.user.id: 
            await interaction.response.send_message ("Хитрый мешок с костями.....")
            user = interaction.user
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

    @discord.app_commands.command (name="help", description="Справка по управлению ботом")
    async def help (self, interaction: discord.Interaction):
        help_view = HelpView(globals.help_commands)
        await interaction.response.send_message("Выберите команду из списка ниже:", view=help_view, ephemeral=True)

async def setup(bot: commands.Bot):
   await bot.add_cog(Commands(bot)) 
   logger.info ("Основной командный модуль загружен.")
   globals.jokes = load_jokes()
   logger.info("База анекдотов загружена")
   globals.memory = load_memory()
   logger.info("Память загружена")
   globals.help_commands = load_help_commands()
   logger.info("Список команд загружен")

class HelpView(discord.ui.View):
    def __init__ (self, commands_list: list[dict[str,str]]):
        self.commands_list = commands_list

        timeout = 300
        super().__init__(timeout=timeout)
        select = discord.ui.Select(
            placeholder="Выберите команду",
            options=[discord.SelectOption(label=command["label"], description=command["short"]) for command in self.commands_list],
                     custom_id="help_command_select"
        )
        select.callback = self.select
        self.add_item(select)

    def build_help_embed(self, command: dict) -> discord.Embed:
        """
        command = {
            "name": str,
            "short": str,
            "description": str,
            "usage": str,
            "example": str
        }
        """
        embed = discord.Embed(
            title=f"📌 Команда /{command['name']}",
            description=command["short"],
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📝 Подробное описание",
            value=command["description"],
            inline=False
        )

        embed.add_field(
            name="⚙ Использование",
            value=f"`{command['usage']}`",
            inline=False
        )

        embed.add_field(
            name="💡 Пример",
            value=f"`{command['example']}`",
            inline=False
        )

        return embed

    async def select(self, interaction: discord.Interaction) -> None:
        #value = interaction.data["values"][0]
        await interaction.response.defer()
        command_name = interaction.data["values"][0]
        #изменить алгоритм поиска команды на более оптимальный, доделать
        command = self.commands_list.index()
        embed = self.build_help_embed(command)
        await interaction.response.edit_message(embed=embed, view=self)

        #await interaction.followup.send(f"You selected {value}", ephemeral=True)

"""class HelpView2(discord.ui.View):
    @discord.ui.select(
        cls=discord.ui.Select,
        options=[discord.SelectOption(label=command["label"], description=command["short"]) for command in self.commands_list],
    )"""

    

    