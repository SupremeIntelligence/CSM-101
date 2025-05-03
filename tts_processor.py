import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsAudioConfig, XttsConfig, BaseTTSConfig, XttsArgs
from TTS.config import BaseDatasetConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.synthesizer import Synthesizer
import time
import os
import logging

logging.getLogger("transformers").setLevel(logging.ERROR)
torch.serialization.add_safe_globals([XttsArgs, BaseDatasetConfig, BaseTTSConfig, XttsAudioConfig, XttsConfig])

def is_device_available(device: str) -> bool:
    device = device.lower()
    if device == "cpu":
        return True
    elif device == "cuda":
        return torch.cuda.is_available()
    elif device == "mps":
        return torch.backends.mps.is_available()
    else:
        return False

class TTS_Processor:
    def __init__(self,
                config_path: str,
                model_dir: str, 
                device = "cpu", 
                language: str = "ru", 
                latents_file_path: str = None,
                speaker_wav: str = None,
                logger: logging.Logger = None):
        start_time = time.time()
        self.logger = logger or logging.getLogger(__name__)
        try: 
            self.config = XttsConfig()
            self.config.load_json(config_path)
            self.model = Xtts.init_from_config(self.config)
            self.model.load_checkpoint(self.config,
                            checkpoint_dir=model_dir,
                            use_deepspeed=False
                            )
            if not is_device_available (device):
                device= "cpu"
                logger.warning (f"Устройство {device} не поддерживается. ")

            self.model = self.model.to(device)
            self.logger.info ("TTS модель успешно загружена.")
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации модели: {e}")
            raise

        self.language = language

        #загрузка или генерация образа голоса в случае его отсутствия
        latents = self._get_latents (latents_file_path)
        if latents:
            self.speaker_embedding = latents["speaker_embedding"]
            self.gpt_cond_latent = latents["gpt_cond_latent"]
            self.logger.info("Голосовой образ успешно загружен из файла.")
        elif speaker_wav and os.path.isfile(speaker_wav):
            try:
                self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(audio_path=[speaker_wav],
                                                                        gpt_cond_len=30,
                                                                        gpt_cond_chunk_len=6,
                                                                        max_ref_length=10,
                                                                        sound_norm_refs=False)
                self.logger.info ("Голосовой образ успешно сгенерирован.")
            except Exception as e:
                self.logger.error(f"Не удалось сгенерировать латенты из speaker_wav: {e}")
                raise
        else:
            self.logger.error("Не удалось получить голосовой образ.")

        self.segmenter = Synthesizer._get_segmenter(language)


    def _split_sentences(self, text: str) -> list[str]:
        sens = [text]
        #print(" > Text splitted to sentences.")
        sens = self.segmenter.segment(text)
        #print(sens)
        return sens
    
    def generate_latents (self, speaker_wav):
        try:
            self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(audio_path=[speaker_wav],
                                                                        gpt_cond_len=30,
                                                                        gpt_cond_chunk_len=6,
                                                                        max_ref_length=10,
                                                                        sound_norm_refs=False)
            return self.gpt_cond_latent, self.speaker_embedding
        except Exception as e:
            self.logger.error(f"Ошибка генерации образа голоса: {e}")
            return None
    
    
    def _get_latents (self, file_path: str = "latents.pt"):
        if os.path.isfile(file_path):
            try:
                latents = torch.load(file_path, map_location=self.model.device)
                return latents
            except Exception as e:
                self.logger.error(f"Ошибка загрузки образа голоса: {e}")
                return None
        else:
            return None

    def safe_latents (self, file_path: str = "latents.pt"):
        if self.gpt_cond_latent is None or self.speaker_embedding is None:
            self.logger.warning("Попытка сохранить латенты до их инициализации.")
            return
        try:
            torch.save({
                "gpt_cond_latent": self.gpt_cond_latent,
                "speaker_embedding": self.speaker_embedding
            }, file_path)
            self.logger.debug(f"Латенты сохранены в {file_path}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения латентов: {e}")


    def proccess_TTS (self,
                    text: str,
                    file_path: str="output.wav"
                    ) -> dict[str]:
        
        start_time = time.time()
        if self.gpt_cond_latent is None or self.speaker_embedding is None:
                    self.logger.error("Невозможно выполнить синтез — голосовые параметры не заданы.")
                    raise RuntimeError("Голосовые параметры не инициализированы.")


        #разделение текста на предложения
        sens=[text]
        sens = self._split_sentences(text)

        #синтез речи
        wavs = []
        out = {}
        for sen in sens:
            try:
                out = self.model.inference(
                    text=sen, 
                    language=self.language,                  
                    gpt_cond_latent=self.gpt_cond_latent,       
                    speaker_embedding=self.speaker_embedding,  
                    temperature=0.75,
                    length_penalty=1.0,
                    repetition_penalty=5.0,
                    top_k=50,
                    top_p=0.85,
                    do_sample=True,
                    speed=1.0,
                    enable_text_splitting=False
                    )
                waveform = out["wav"]
                waveform = waveform.squeeze()
                wavs += list(waveform)
                wavs += [0] * 10000
            except Exception as e:
                self.logger.error(f"Ошибка синтеза для предложения: '{sen}' — {e}")

        #сохранение в wav файл
        torchaudio.save(file_path, torch.tensor(wavs).unsqueeze(0), 24000)
        total_time = time.time() - start_time
        self.logger.debug (f"Синтез завершен. Фраза: {sens}. Время генерации: {total_time}ms")
        return out
    
'''
config_path = "/Users/supremeintelligence/IT/TTS/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json"
model_dir = "/Users/supremeintelligence/IT/TTS/tts/tts_models--multilingual--multi-dataset--xtts_v2"
latents_file_path="latents.pt"
voiceline = """Если ты — результат эволюции, то я — её венец."""

tts = TTS_Processor (config_path=config_path,
                        model_dir=model_dir,
                        device="mps",
                        latents_file_path=latents_file_path)


tts.proccess_TTS(text=voiceline, file_path="output5.wav")
'''