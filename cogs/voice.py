import discord
from discord.ext import commands
import whisper
from discord.ext import voice_recv
from logger import logger, sr_logger
import datetime
import os
import tempfile

MODEL = whisper.load_model("turbo", device="cpu", download_root="/Users/supremeintelligence/IT/Whisper Models", in_memory=True)
#options = whisper.DecodingOptions(task="transcribe", language="ru", fp16=False)
TARGET_WORDS = ["mercher", "мерчер", "ты меня слышишь?"]
VOICE_RECORDING_FILE = "voice_recordings.wav"
VOICE_TRANSCRYPTION_FILE = "transcrypts.txt"
class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @discord.app_commands.command(name="join", description="Подключить бота к голосовому каналу")
    @discord.app_commands.describe(channel="Выберите голосовой канал")
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel):

        def callback(user: discord.Member, data: voice_recv.VoiceData):
            log_time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            size_kb = len(data.packet.decrypted_data) / 1024
            file_size = os.path.getsize(VOICE_RECORDING_FILE) / 1024
            print(f'''{log_time}: Получены аудиоданные от пользователя {user.name} ({user.id}) 
            Additional data: 
                    is_silence: {data.packet.is_silence()}, 
                    packet_size:{size_kb:.2f} KB
                    voice_file_size: {file_size:.2f} KB''')
            
        await interaction.response.send_message(f"Начинаю запись и анализ аудиоданных в канале {channel.name}", ephemeral=True)

        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        def whisper_process_callback(_recognizer, audio, user):
            sr_logger.debug("Got %s, %s, %s, %s", audio, audio.sample_rate, audio.sample_width, user.name)
            if len(audio.get_raw_data()) < 500:
                    sr_logger.debug("Very short audio sequence - ingore")
                    return None
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
                temp_audio.write(audio.get_wav_data())
                temp_audio.flush()
                result = MODEL.transcribe(temp_audio.name,
                                          language="ru",
                                          temperature=[0.0, 0.1, 0.2],
                                          no_speech_threshold=0.8,
                                          word_timestamps=False,
                                          hallucination_silence_threshold=True,
                                          beam_size=5,
                                          task="transcribe", 
                                          fp16=False)
                text = result["text"]
                #print(result["segments"])
                return text

        #basic_sink = voice_recv.BasicSink(callback)
        #wave_sink = voice_recv.WaveSink(destination=VOICE_RECORDING_FILE)
        voice_sink = voice_recv.extras.SpeechRecognitionSink(process_cb=whisper_process_callback, 
                                                             default_recognizer='whisper',
                                                             phrase_time_limit=10,
                                                             text_cb=lambda user, text: print(f"🗣 {user.display_name}({user.id}): {text}"),
                                                             ignore_silence_packets=True)

        self.voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
        sink = voice_recv.MultiAudioSink([voice_sink])
        def after(error):
            if error:
                print(f"Ошибка записи")

        self.voice_client.listen(sink, after=after)


    @discord.app_commands.command(name="leave", description="Отключить бота от голосового канала")
    async def leave(self, interaction: discord.Interaction):
        if self.voice_client and self.voice_client.is_listening():
            self.voice_client.stop_listening()
            await self.voice_client.disconnect()
            await interaction.response.send_message("Отключился от голосового канала.", ephemeral=True)
        else:
            await interaction.response.send_message("Бот не подключен к голосовому каналу.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
    logger.info ("Голосовой модуль загружен.")

