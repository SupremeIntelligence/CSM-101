import discord
from discord.ext import commands
from logger import logger
import asyncio
import sys
import os

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.mode = False

    @discord.app_commands.command(name="maintenance", description="Включает/выключает режим техобслуживания")
    @discord.app_commands.describe(mode="Выберите режим")
    @discord.app_commands.checks.has_role("Supreme Intelligence")
    async def maintenance(self, interaction: discord.Interaction, mode: bool):
        self.bot.mode = mode
        if self.bot.mode:
            status = "включен."
            custom_actvity = discord.CustomActivity(name="В процессе технического апгрейда")
            await self.bot.change_presence(status=discord.Status.idle, activity=custom_actvity)
        else:
            status = "выключен."
            custom_activity = discord.CustomActivity(name="Следит за Мерчером 👀")
            await self.bot.change_presence(status=discord.Status.online, activity=custom_activity)
            
        await interaction.response.send_message(f"Режим техобслуживания {status}", ephemeral=True)
    
    @commands.hybrid_command(name="shutdown", description="Выключение бота")
    @commands.has_role("Supreme Intelligence")
    async def shutdown(self, ctx):
        await ctx.send("Выключение бота")
        await asyncio.sleep(10)
        await self.bot.close()


    @commands.hybrid_command(name="restart", description="Перезапуск бота")
    @commands.has_role("Supreme Intelligence")
    async def restart(self, ctx: commands.Context):
        await ctx.send("Перезапуск систем... ")
        python = sys.executable  
        os.execv(python, [python] + sys.argv) 

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.info (f"Команда '{ctx.command}' вызвана пользователем {ctx.author}, канал: {ctx.channel}")
        if self.bot.mode and ctx.command.name != "maintenance":
            await ctx.send("Бот в режиме тех. обслуживания.", ephemeral=True)
            raise commands.CommandsError("Бот в режиме тех. обслуживания.")
        
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        logger.info (f"Команда '{interaction.command.name}' вызвана пользователем {interaction.user.display_name}, канал: {interaction.channel}")
        if self.bot.mode and interaction.command and interaction.command.name != "maintenance":
             if not interaction.response.is_done():
                await interaction.response.defer()  
                await interaction.followup.send("Бот в режиме тех. обслуживания.", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member == self.bot.user:
            if before.channel is None and after.channel is not None:
                logger.info(f"Бот подключился к голосовому каналу {after.channel.name}")
            elif before.channel is not None and after.channel is None:
                logger.info(f"Бот отключился от канала {before.channel.name}")

async def setup(bot):
   await bot.add_cog(Maintenance(bot)) 
   
