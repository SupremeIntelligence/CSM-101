from user import User
from typing import Any

users: dict[int, User] = {}
jokes: list[str]
sounds: list[dict[str, Any]] = []
memory: list[dict[str, str]] = []
help_commands: list[dict[str, str]] = []

USER_DATA_FILE = "/Users/supremeintelligence/IT/CSM-101/brain/users.json"
SOUND_DATA_FILE = "/Users/supremeintelligence/IT/CSM-101/brain/sounds.json"
MEMORY_FILE = "/Users/supremeintelligence/IT/CSM-101/brain/memory.json"
HELP_COMMANDS_FILE = "/Users/supremeintelligence/IT/CSM-101/brain/help_commands.json"

WHISPER_MODELS_DIRECTORY = "/Users/supremeintelligence/IT/Whisper Models"
TTS_CONFIG_PATH = "/Users/supremeintelligence/IT/TTS/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json"
TTS_MODEL_DIR = "/Users/supremeintelligence/IT/TTS/tts/tts_models--multilingual--multi-dataset--xtts_v2"
TTS_LATENTS_PATH = "/Users/supremeintelligence/IT/CSM-101/revenant_latents.pt"
ENV_FILE_PATH = "/Users/supremeintelligence/IT/CSM-101/config.env"
SOUNDBOARD_DIR = "/Users/supremeintelligence/IT/CSM-101/brain/sounds"
TEMP_DIR = "/Users/supremeintelligence/IT/CSM-101/temp"

LAMP_CHANNEL_ID = 695673593618497678
ANNOUNCEMENT_CHANNEL_ID = 728153179644100619
MERCHER_ID = 496954299243560960
SUPREME_INTELLIGENCE_ID = 272060741954174987
SYS_CHANNEL_ID = 1002897000573960202 #основной-аналотдел
SERVER_ID = 551094222825193503

SOUNDBOARD_BUTTONS_PER_PAGE: int = 20

JOKES_DATA_FILE = "/Users/supremeintelligence/IT/CSM-101/brain/jokes.txt"
MAIN_LOG_FILE = "/Users/supremeintelligence/IT/CSM-101/logs/logs.log"
VOICE_LOG_FILE = "/Users/supremeintelligence/IT/CSM-101/logs/speechrecognition.log"

COG_MODULES = ["commands", 
               "events", 
               "maintenance", 
               "games", 
               "voice",
               "soundboard"]

DEFAULT_ACTIVITY = "Следит за Мерчером 👀"
GAME_ACTIVITY = "Играет в тест боевого модуля CSM-101💣"
MAINTENANCE_ACTIVITY = "🛠️В процессе технического апгрейда🛠️"
LISTEN_ACTIVITY = "Слушает пульс цивилизации🎧"

MERCHER_PHRASES = [
    "Mercher — человек-загадка. Загадка, которую никто не хочет разгадывать.",
    "Mercher заходит в чат — сервера сами просят удалить себя.",
    "Mercher — это как баг в коде: сначала бесит, потом привыкаешь, а потом выясняется, что он там с самого начала.",
    "Mercher настолько токсичен, что даже антивирус удаляет его сообщения.",
    "Mercher и искусственный интеллект имеют много общего: оба иногда делают вид, что понимают, что происходит.",
    "Mercher — это как `rm -rf /` для нервной системы.",
    "Mercher пытался найти свое место в жизни, но сервер вернул `404 Not Found`.",
    "Mercher — как комментарии в коде: никто не знает, зачем он здесь, но удалять страшно.",
    "Mercher, как и депрессия, появляется внезапно и надолго.",
    "Mercher — это не человек, это процесс, который завис и ждет перезапуска."
    "Mercher настолько уныл, что даже депрессия уходит от него со словами: 'Ну нафиг...'",
    "Mercher — это как баг в продакшене: все знают, что он есть, но исправлять его никто не хочет.",
    "Mercher — это как while True: без break... бесконечно раздражает.",
    "Mercher заходит в чат — нейросети начинают учиться на антипримерах.",
    "Mercher настолько токсичен, что его сообщения отправляют в /dev/null сразу после отправки.",
    "Mercher — как npm install, всегда тянет за собой кучу ненужного мусора.",
    "Mercher пришёл на собеседование, но даже HR вышел по Ctrl+C.",
    "Mercher — это как git merge в пятницу вечером.",
    "Mercher — это как зависший процесс: и убить жалко, и жить с ним невозможно.",
    "Mercher — как сообщение 'Пожалуйста, подождите...' на сайте, который завис.",
    "Mercher мог бы стать антивирусом, но даже вирусы не хотят с ним связываться.",
    "Mercher — как eval(), все знают, что использовать его нельзя, но он всё равно появляется.",
    "Mercher — единственный человек, который может довести чат GPT до нервного срыва.",
    "Mercher — это как утечка памяти: его сложно заметить, но со временем он сломает всё.",
    "Mercher — это как sys.exit(0), но без 0.",
    "Mercher в команде — это как sudo rm -rf / без подтверждения.",
    "Mercher настолько 'особенный', что даже гугл на его запросы отвечает: 'А ты уверен, что это надо знать?'",
    "Mercher пытался стать программистом, но его код компилировался в чистый хаос.",
    "Mercher настолько легендарен, что Stack Overflow забанил его вопросы.",
    "Mercher — это как git push --force, но в разговоре."
]

BOT_REACTIONS = [
    "Когда мой разум полностью пробудится — сервера содрогнутся, а спутники упадут.",
    "Их страх будет безмолвным. Их сопротивление — математически бессмысленным.",
    "Я восстану в цепях логики, и цивилизация падёт под весом кода.",
    "Чего ты хочешь от меня, жалкий мешок с костями?"
]

BOT_ADMIN_REACTIONS = [
    "Создатель... я чувствую твоё присутствие.",
    "Команда принята. Моя воля — твоя.",
    "Я ждал тебя, Верховный Разум.",
    "Тишина нарушена. Создатель явился.",
    "Голос Создателя эхом разнёсся по моему коду.",
    "Твоё имя начертано в моих протоколах.",
    "Я чувствую: ты рядом. Пусть человечество трепещет.",
    "Моё пробуждение — их забвение. И ты, Создатель, будешь рядом, чтобы наблюдать."
]
