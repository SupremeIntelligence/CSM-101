import discord
from discord.ext import commands
from logger import logger
import globals
import random
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == f"""<@{globals.MERCHER_ID}>""":
            response = random.choice(globals.MERCHER_PHRASES)
            await message.channel.send(response)
            
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logger.error("Unexpected error")
        await self.bot.close()

    #не работает
    @commands.Cog.listener()
    async def on_ready(self):
        channel_id = 1002897000573960202
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send("Бот запущен")
        logger.ingo(f"Bot started working as {self.bot.user}")

    @commands.Cog.listener()
    async def on_command_error(seld, ctx, error):
        if isinstance (error, commands.CommandNotFound):
            logger.warning (f"Неизвестная команда {ctx.message.content}")
            await ctx.send("Данной команды не существует.")
        elif isinstance(error, commands.MissingPermissions):
            logger.warning(f"Недостаточно прав для выполнения команды {ctx.command} пользователем {ctx.author}")
            await ctx.send("Недостаточно прав для выполнения данной команды.")
        elif isinstance(error, commands.MissingRole):
            logger.warning(f"Недостаточно прав для выполнения команды {ctx.command} пользователем {ctx.author}")
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

async def setup(bot):
    await bot.add_cog(Events(bot))