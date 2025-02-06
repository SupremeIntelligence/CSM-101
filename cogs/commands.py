import discord
from discord.ext import commands
import asyncio
import sys
import os
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
        message = """<@496954299243560960>, как дела?```diff
+ ░▒█▀▄▀█░▒█▀▀▀░▒█▀▀▄░▒█▀▀▄░▒█░▒█░▒█▀▀▀░▒█▀▀▄
- ░▒█▒█▒█░▒█▀▀▀░▒█▄▄▀░▒█░░░░▒█▀▀█░▒█▀▀▀░▒█▄▄▀
+ ░▒█░░▒█░▒█▄▄▄░▒█░▒█░▒█▄▄▀░▒█░▒█░▒█▄▄▄░▒█░▒█
```"""
        await interaction.response.send_message(message)

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

async def setup(bot):
   await bot.add_cog(Commands(bot)) 
   
