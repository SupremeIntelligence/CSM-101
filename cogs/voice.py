import discord
from discord.ext import commands
import whisper
from discord.ext import voice_recv
from logger import logger, sr_logger
from globals import WHISPER_MODELS_DIRECTORY, SYS_CHANNEL_ID
import datetime
import os
import tempfile
from collections import deque
import asyncio
import torch
from enum import Enum, auto
import platform
import whisper_processor
import time
import concurrent.futures

TARGET_WORDS = ["mercher", "мерчер", "ты меня слышишь?"]
VOICE_RECORDING_FILE = "voice_recordings.wav"
#VOICE_TRANSCRYPTION_FILE = "brain/transcrypts.txt"
class Backend(Enum):
    WHISPER_MACOS = auto()
    WHISPER_CUDA = auto()
    WHISPER_CPU = auto()

def get_device() -> Backend:
    if platform.system() == "Darwin":
        logger.info("WHISPER_MACOS: Using whisper.cpp")
        return Backend.WHISPER_MACOS
    elif torch.backends.cuda.is_availible():
        logger.info ("WHISPER_CUDA: CUDA is availible. Using OpenAI WhisperAI")
        return Backend.WHISPER_CUDA
    else:
        logger.info("WHISPER_CPU: Using OpenAI WhisperAI on CPU")
        return Backend.WHISPER_CPU
    
class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.transcripts = deque (maxlen=5)
        self.loop = asyncio.get_running_loop()
        self.device = get_device()
        if self.device == Backend.WHISPER_MACOS:
            self.MODEL = None
        elif self.device == Backend.WHISPER_CUDA:
            self.MODEL = whisper.load_model("base", device="cuda", download_root=WHISPER_MODELS_DIRECTORY)
        else:
            self.MODEL = whisper.load_model("base", device="cpu", download_root=WHISPER_MODELS_DIRECTORY)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2) #Thread Pool for intensive tasks

    def speech_tracing(self) -> str:
        content = ["### Трассировка реплик: "]
        for t in self.transcripts:
            content.append(f"> 👤 *{t["user"]}:* ```- {t["text"]}```")
        joined_content = "\n".join(content)
        return joined_content

    @discord.app_commands.command(name="join", description="Подключить бота к голосовому каналу")
    @discord.app_commands.describe(channel="Выберите голосовой канал")
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel):

        def audio_info_callback(user: discord.Member, data: voice_recv.VoiceData):
            log_time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            size_kb = len(data.packet.decrypted_data) / 1024
            file_size = os.path.getsize(VOICE_RECORDING_FILE) / 1024
            print(f'''{log_time}: Получены аудиоданные от пользователя {user.name} ({user.id}) 
            Additional data: 
                    is_silence: {data.packet.is_silence()}, 
                    packet_size:{size_kb:.2f} KB
                    voice_file_size: {file_size:.2f} KB''')
            
        message = await interaction.response.send_message(f"Начинаю запись и анализ аудиоданных в канале {channel.name}", ephemeral=True)
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        async def async_whisper_process_callback(_recognizer, audio, user):
            raw_data = audio.get_raw_data()
            if len(raw_data) < 4000:
                    #sr_logger.debug("Ignoring very short audio sequence.")
                    return None
            #sr_logger.debug("Got audio data %s, %s from %s",  audio.sample_rate, audio.sample_width, user.name)

            start_time = time.time()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
                temp_audio.write(audio.get_wav_data())
                temp_audio.flush()
                try:
                    if self.device == Backend.WHISPER_MACOS:
                        sr_logger.debug("Using CoreML backend for Whisper.cpp")
                        result = await self.loop.run_in_executor (
                            self.executor,
                            whisper_processor.process_audio,
                            temp_audio.name,
                            "small")
                    else:
                        sr_logger.debug("Using default Whisper model")
                        def transcribe ():
                            return self.MODEL.transcribe(temp_audio.name,
                                                        language="ru",
                                                        temperature=[0.0, 0.1, 0.2],
                                                        no_speech_threshold=0.8,
                                                        word_timestamps=False,
                                                        hallucination_silence_threshold=True,
                                                        beam_size=3,
                                                        task="transcribe", 
                                                        fp16=False)
                        
                        result = await self.loop.run_in_executor(
                            self.executor,
                            transcribe)
                        result = result["text"]
                except Exception as e:
                    sr_logger.error ("Error processing speech using Whisper")
                    return None
                
                finally:
                    elapsed = time.time() - start_time
                    duration_seconds = len(raw_data) / (audio.sample_rate * audio.sample_width)
                    sr_logger.info(f"Processed audio data: {len(raw_data)}B ({len(raw_data)/1024:.2f} KB), duration≈{duration_seconds:.2f}s, elapsed={elapsed}s")
                    return result
                    #print(result["segments"])

        def whisper_process_callback (_recognizer, audio, user):
            coro = async_whisper_process_callback(_recognizer, audio, user)
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            try:
                return future.result()
            except Exception as e:
                sr_logger.error(f"Whisper_process_callback error: {e}")
            return None
        
        #basic_sink = voice_recv.BasicSink(callback)
        #wave_sink = voice_recv.WaveSink(destination=VOICE_RECORDING_FILE)

        async def voice_rec_callback (user: discord.User, text: str):
            sr_logger.info (f"User {user} ({user.id}) said {text} ")
            self.transcripts.append ({"user":user.display_name, "text": text})
            print(f"🗣 {user.display_name}({user.id}): {text}")
            await interaction.edit_original_response(content=self.speech_tracing())

        voice_sink = voice_recv.extras.SpeechRecognitionSink(process_cb=whisper_process_callback, 
                                                             default_recognizer='whisper',
                                                             phrase_time_limit=11,
                                                             text_cb=lambda user, text: asyncio.run_coroutine_threadsafe(
                                                                                voice_rec_callback(user, text), self.loop),
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

