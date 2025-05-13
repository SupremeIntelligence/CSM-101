import discord
from discord.ext import commands
from logger import logger
import globals
import random
from utils import set_activity
class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            bot_mention = message.guild.me.mention
        else:
            bot_mention = self.bot.user.mention

        if message.content == f"""<@{globals.MERCHER_ID}>""":
            response = random.choice(globals.MERCHER_PHRASES)
            await message.channel.send(response)
        elif message.content.strip() == bot_mention:
            await message.channel.send ("Чего ты хочешь от меня, жалкий мешок с костями?")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logger.error("Unexpected error")
        await self.bot.close()

    #Работает при реконнектах
    @commands.Cog.listener()
    async def on_ready(self):
        await set_activity(self.bot, activity_text=globals.LISTEN_ACTIVITY, activity_type=discord.ActivityType.listening)
        """channel = self.bot.get_channel(globals.SYS_CHANNEL_ID)
        if channel:
            await channel.send("Бот перезапущен", silent=True)"""
        logger.info(f"Бот перезапустил работу.")
    
    @commands.Cog.listener()
    async def on_connect(self):
        logger.info("Бот подключился к Discord.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger.warning("Бот отключился от Discord.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance (error, commands.CommandNotFound):
            logger.warning (f"Неизвестная команда {ctx.message.content}")
            await ctx.send("Данной команды не существует.")
        elif isinstance(error, commands.MissingPermissions):
            logger.warning(f"Недостаточно прав для выполнения команды {ctx.command} пользователем {ctx.author}", ephemeral=True)
            await ctx.send("Недостаточно прав для выполнения данной команды.")
        elif isinstance(error, commands.MissingRole):
            logger.warning(f"Недостаточно прав для выполнения команды {ctx.command} пользователем {ctx.author}", ephemeral=True)
            await ctx.send("Недостаточно прав для выполнения данной команды.")
        else:
            logger.error (f"Произошла неизвестная ошибка - Команда: {ctx.command}, сообщение: {ctx.message.content}, пользователь: {ctx.author}, канал: {ctx.channel}")
            await ctx.send("Произошла неизвестная ошибка.")


    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.CommandNotFound):
            logger.warning(f"Неизвестная команда {interaction.command}")
            await interaction.response.send_message("Данной команды не существует.", ephemeral=True)

        elif isinstance(error, discord.app_commands.MissingPermissions):
            logger.warning(f"Недостаточно прав для выполнения команды {interaction.command} пользователем {interaction.user}")
            await interaction.response.send_message("Недостаточно прав для выполнения данной команды.", ephemeral=True)

        elif isinstance(error, discord.app_commands.MissingRole):
            logger.warning(f"Недостаточно прав для выполнения команды {interaction.command} пользователем {interaction.user}")
            await interaction.response.send_message("Недостаточно прав для выполнения данной команды.", ephemeral=True)

        else:
            logger.error(f"Произошла неизвестная ошибка - Команда: {interaction.command}, пользователь: {interaction.user}, канал: {interaction.channel}")
            await interaction.response.send_message("Произошла неизвестная ошибка.", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member == self.bot.user:
            if before.channel is None and after.channel is not None:
                logger.info(f"Бот подключился к голосовому каналу {after.channel.name}")
            elif before.channel is not None and after.channel is None:
                logger.info(f"Бот отключился от канала {before.channel.name}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
    logger.info("Модуль ивентов загружен.")
    