import discord
from discord.ext import commands
import whisper
import asyncio
import wave
import globals
import ffmpeg

MODEL = whisper.load_model("turbo")
TARGET_WORDS = ["mercher", "мерчер", "ты меня слышишь?"]

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="join", description="Подключить бота к голосовому каналу")
    @discord.app_commands.describe(channel="Выберите голосовой канал")
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
        vc = await channel.connect()
        await interaction.response.send_message(f"Начинаю запись и анализ аудиоданных в канале {channel.name}")


    @discord.app_commands.command(name="leave", description="Отключить бота от голосового канала")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Отключился от голосового канала.")
        else:
            await interaction.response.send_message("Бот не подключен к голосовому каналу.", ephemeral=True)


# def save_audio(user, sink):
#     """Сохраняет аудио в файл."""

#     audio_data = sink.audio_data(user)
#     if audio_data is None:
#         return

#     filename = f"{user.name}_{user.id}.pcm"
#     with open(filename, "wb") as f:
#         f.write(audio_data.pcm)

#     # Преобразование в формат .wav (опционально)
#     wav_filename = f"{user.name}_{user.id}.wav"
#     ffmpeg.input(filename, format='s16le', acodec='pcm_s16le', ac=2, ar='48k').output(wav_filename).run()

#     print(f"Аудио пользователя {user.name} сохранено в {wav_filename}")

async def setup(bot):
    await bot.add_cog(Voice(bot))

