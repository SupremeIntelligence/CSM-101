import discord
from discord.ext import commands
import whisper
from discord.ext import voice_recv
import datetime
import asyncio
import wave
import globals
import ffmpeg

MODEL = whisper.load_model("turbo")
TARGET_WORDS = ["mercher", "мерчер", "ты меня слышишь?"]

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
    
    @discord.app_commands.command(name="join", description="Подключить бота к голосовому каналу")
    @discord.app_commands.describe(channel="Выберите голосовой канал")
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        def callback(user: discord.Member, data: voice_recv.VoiceData):
            log_time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            print(f"{log_time}:Получены аудиоданные от пользователя {user.name} ({user.id}) ")

        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        sink = voice_recv.WaveSink(destination="voice_recordings.wav")
        self.voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
        def after(error):
            log_time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            if error:
                print(f"{log_time} Ошибка записи: {error}")
            else:
                print(f"{log_time} Запись завершена")

        self.voice_client.listen(sink, after=after)

        await interaction.response.send_message(f"Начинаю запись и анализ аудиоданных в канале {channel.name}")


    @discord.app_commands.command(name="leave", description="Отключить бота от голосового канала")
    async def leave(self, interaction: discord.Interaction):
        if self.voice_client and self.voice_client.is_listening():
            self.voice_client.stop_listening()
            await self.voice_client.disconnect()
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

