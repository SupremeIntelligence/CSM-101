import globals
from logger import logger
import random

def load_jokes(filename = globals.JOKES_DATA_FILE):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
    
            return content.split("\n///...///\n")
            
    except FileNotFoundError:
        logger.critical("Файл анекдотов не найден.")
    except Exception as e:
        logger.critical(f"Ошибка при получении анекдота: {e}")

def get_joke(jokes: list[str]):
    return random.choice(jokes)