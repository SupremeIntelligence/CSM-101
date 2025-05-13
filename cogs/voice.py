import discord
from discord.ext import commands
import whisper
from discord.ext import voice_recv
from logger import logger, sr_logger
from globals import WHISPER_MODELS_DIRECTORY, TTS_MODEL_DIR, TTS_CONFIG_PATH, TTS_LATENTS_PATH
import os
import tempfile
from collections import deque
import asyncio
import torch
from enum import Enum, auto
import platform
import whisper_processor
import time
from concurrent.futures import ThreadPoolExecutor
from tts_processor import TTS_Processor
import re

TARGET_WORDS = ["mercher", "мерчер", "ты меня слышишь?"]
VOICE_RECORDING_FILE = "voice_recordings.wav"
class Backend(Enum):
    MACOS = auto()
    CUDA = auto()
    CPU = auto()

def get_device() -> Backend:
    if platform.system() == "Darwin":
        logger.debug("WHISPER_MACOS: Using whisper.cpp")
        return Backend.MACOS
    elif torch.backends.cuda.is_available():
        logger.debug ("WHISPER_CUDA: CUDA is availible. Using OpenAI WhisperAI")
        return Backend.CUDA
    else:
        logger.debug("WHISPER_CPU: Using OpenAI WhisperAI on CPU")
        return Backend.CPU
    
class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_client = None
        self.transcripts = deque (maxlen=5)
        self.loop = asyncio.get_running_loop()
        self.device = get_device()
        
        self.stt_executor = ThreadPoolExecutor(max_workers=os.cpu_count()/2) #Thread Pool for STT tasks
        self.tts_executor = ThreadPoolExecutor(max_workers=1) #Thread Pool for TTS tasks
        self.STT = None
        self.TTS = None

    async def _init_STT(self):
        def _initialize_STT(device: str = "cpu"):
            return whisper.load_model("base", device=device, download_root=WHISPER_MODELS_DIRECTORY)
        
        if self.device == Backend.MACOS:
            self.STT = None
        elif self.device == Backend.CUDA:
            self.STT = await self.loop.run_in_executor(
                self.stt_executor,
                _initialize_STT,
                self.device.name.lower()
            )
        else:
            self.STT = await self.loop.run_in_executor(
                self.stt_executor,
                _initialize_STT
            )

    async def _init_TTS(self):
        def _initialize_TTS():
            return TTS_Processor(
                config_path=TTS_CONFIG_PATH,
                model_dir=TTS_MODEL_DIR,
                device="mps",
                language="ru",
                latents_file_path=TTS_LATENTS_PATH,
                logger=sr_logger
            )
        self.TTS = await self.loop.run_in_executor(
            self.tts_executor,
            _initialize_TTS
        )

    def _speech_tracing(self) -> str:
        content = ["### Трассировка реплик: "]
        for t in self.transcripts:
            content.append(f"> 👤 *{t['user']}:* ```- {t['text']}```")
        joined_content = "\n".join(content)
        return joined_content

    def _whisper_process_callback (self, _recognizer, audio, user):
            coro = self._async_whisper_process_callback(_recognizer, audio, user)
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            try:
                return future.result()
            except Exception as e:
                sr_logger.error(f"Whisper_process_callback error: {e}")
            return None
    
    async def _async_whisper_process_callback(self, _recognizer, audio, user):
        raw_data = audio.get_raw_data()
        if len(raw_data) < 4000:
                #sr_logger.debug("Ignoring very short audio sequence.")
                return None
        result = None
        start_time = time.time()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
            temp_audio.write(audio.get_wav_data())
            temp_audio.flush()
            try:
                if self.device == Backend.MACOS:
                    #sr_logger.debug("Using CoreML backend for Whisper.cpp")
                    result = await self.loop.run_in_executor (
                        self.stt_executor,
                        whisper_processor.process_audio,
                        temp_audio.name,
                        "small")
                else:
                    def transcribe ():
                        return self.STT.transcribe(temp_audio.name,
                                                    language="ru",
                                                    temperature=[0.0, 0.1, 0.2],
                                                    no_speech_threshold=0.8,
                                                    word_timestamps=False,
                                                    hallucination_silence_threshold=True,
                                                    beam_size=3,
                                                    task="transcribe", 
                                                    fp16=False)
                    
                    result = await self.loop.run_in_executor(
                        self.stt_executor,
                        transcribe)
                    result = result["text"]
            except Exception as e:
                sr_logger.error ("Error processing speech using Whisper")
                return None
            
            finally:
                elapsed = time.time() - start_time
                duration_seconds = len(raw_data) / (audio.sample_rate * audio.sample_width)
                backend = ""
                model_name = ""
                if self.device == Backend.MACOS:
                    backend = "CoreMl"
                    model_name = "whisper.cpp"
                else:
                    backend = f"{self.device.name.lower()}"
                    model_name = "OpenAI Whisper"

                sr_logger.info(f"Processed audio data: size={len(raw_data)/1024:.2f} KB, duration≈{duration_seconds:.2f}s, elapsed={elapsed}s, backend={backend}, model={model_name}")
                return result
                #print(result["segments"])   

    async def _response (self, text=str):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name
            try:
                try:
                    await self.loop.run_in_executor(self.tts_executor, self.TTS.proccess_TTS, text, temp_path)
                    audio = discord.FFmpegPCMAudio(temp_path)
                    if self.voice_client.is_playing():
                        await asyncio.sleep(0.5)
                    self.voice_client.play(audio)
                except Exception as e:
                    sr_logger.error(f"TTS ошибка: {e}")
                    return
                sr_logger.info(f"🤖 Бот произнес фразу '{text}' в голосовом канале {self.voice_client.channel}")
                print (f"🤖 Бот произнес фразу '{text}' в голосовом канале {self.voice_client.channel}")
                while self.voice_client.is_playing():
                    await asyncio.sleep(0.5)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    @discord.app_commands.command(name="join", description="Подключить бота к голосовому каналу")
    @discord.app_commands.describe(channel="Выберите голосовой канал", listen="Включение/выключение системы распознавания речи")
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel, listen: bool = False):
            
        await interaction.response.send_message(f"Начинаю запись и анализ аудиоданных в канале {channel.name}", ephemeral=True)
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        async def _voice_rec_callback (user: discord.User, text: str):
            sr_logger.info (f"🗣 Пользователь {user} ({user.id}) произнес '{text}' ")
            self.transcripts.append ({"user":user.display_name, "text": text})
            print(f"🗣 {user.display_name}({user.id}): {text}")
            await interaction.edit_original_response(content=self._speech_tracing())
            '''pattern = r"(Бот|Мерчер|Вот),?\s*дай\s+зву[ка]"
                if re.search(pattern=pattern, string=result, flags=re.IGNORECASE):
                    print ("smth")
                    await self.response("Мерчер, пошел в пизду")'''

        voice_sink = voice_recv.extras.SpeechRecognitionSink(process_cb=self._whisper_process_callback, 
                                                            default_recognizer='whisper',
                                                            phrase_time_limit=11,
                                                            text_cb=lambda user, text: asyncio.run_coroutine_threadsafe(
                                                                                _voice_rec_callback(user, text), self.loop),
                                                            ignore_silence_packets=True)

        self.voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)

        sink = voice_recv.MultiAudioSink([voice_sink])
        sr_logger.debug (f"Система распознавания голоса: {listen}")
        if listen:
            self.voice_client.listen(sink)


    @discord.app_commands.command(name="leave", description="Отключить бота от голосового канала")
    async def leave(self, interaction: discord.Interaction):
        if self.voice_client:
            self.voice_client.stop_listening()
            await self.voice_client.disconnect()
            await interaction.response.send_message("Отключился от голосового канала.", ephemeral=True)
        else:
            await interaction.response.send_message("Бот не подключен к голосовому каналу.", ephemeral=True)

    @discord.app_commands.command(name="say", description="Позволяет произнести введенную фразу в голосовом канале.")
    @discord.app_commands.describe(text="Введите текст, который бот должен озвучить")
    async def say(self, interaction: discord.Interaction, text: str):
        if not self.voice_client:
            await interaction.response.send_message("Бот должен быть подключен к голосовому каналу.", ephemeral=True)
            return
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            await interaction.response.defer(ephemeral=True, thinking=True)
            temp_path = tmp.name
            try:
                try:
                    await self.loop.run_in_executor(self.tts_executor, self.TTS.proccess_TTS, text, temp_path)
                    audio = discord.FFmpegPCMAudio(temp_path)
                    if self.voice_client.is_playing():
                        self.voice_client.stop()
                    self.voice_client.play(audio)
                except Exception as e:
                    await interaction.followup.send("Ошибка при генерации или воспроизведении аудио.", ephemeral=True)
                    sr_logger.error(f"TTS ошибка: {e}")
                    return
                await interaction.followup.send(f"Я сказал: `{text}`", ephemeral=True)
                sr_logger.info(f"Бот произнес фразу '{text}' в голосовом канале {self.voice_client.channel} по запросу пользователя {interaction.user.display_name}")
                print (f"🤖 Бот произнес фразу '{text}' в голосовом канале {self.voice_client.channel} по запросу пользователя {interaction.user.display_name}")
                while self.voice_client.is_playing():
                    await asyncio.sleep(0.5)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)


async def setup(bot: commands.Bot):
    cog = Voice(bot)
    await bot.add_cog(cog)
    logger.info ("Голосовой модуль загружен.")
    await cog._init_TTS()
    await cog._init_STT()
    logger.info ("STT и TTS модели инициализированы.")

