import logging
from globals import MAIN_LOG_FILE, VOICE_LOG_FILE
def startLogging(name: str = "default", level = logging.DEBUG, filename: str = "default.log", CLI: bool = False) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)

    #logging.basicConfig(level=logging.INFO, filename = "logs.log", filemode="a",
    #                     format="%(asctime)s %(levelname)s %(message)s") #a - режим дозаписи (append)
    
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    
    if CLI:
        CLI_handler = logging.StreamHandler()
        CLI_handler.setLevel(level+10)                                   # В консоли показываем только INFO и выше
        CLI_handler.setFormatter(formatter)
        logger.addHandler(CLI_handler)

    file_handler = logging.FileHandler(filename, encoding="utf-8")    #a - режим дозаписи (append)
    file_handler.setLevel(level)  
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

logger = startLogging("Discord Bot", level=logging.DEBUG, filename=MAIN_LOG_FILE, CLI=True)
sr_logger = startLogging("Speech Recognition", level=logging.DEBUG, filename=VOICE_LOG_FILE)
logging.getLogger("discord.ext.voice_recv.reader").setLevel(logging.WARNING)
