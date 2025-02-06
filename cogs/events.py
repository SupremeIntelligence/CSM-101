import discord
from discord.ext import commands
from logger import logger

#аналотдел-основной ID: 1002897000573960202
#Mercher ID = 496954299243560960
#Ламповая Флудилка ID = 695673593618497678

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == 'ping':
            await message.channel.send('pong')
            
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
            #await channel.send("<@496954299243560960>, как дела?")
            await channel.send("Бот запущен")
        logger.ingo(f"Bot started working as {self.bot.user}")

    @commands.Cog.listener()
    async def on_command_error(seld, ctx, error):
        if isinstance (error, commands.CommandNotfound):
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