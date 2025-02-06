import logging

def startLogging():

    logger = logging.getLogger("Discord Bot")
    logger.setLevel(logging.INFO)

    #logging.basicConfig(level=logging.INFO, filename = "logs.log", filemode="a",
    #                     format="%(asctime)s %(levelname)s %(message)s") #a - режим дозаписи (append)
    
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    
    CLI_handler = logging.StreamHandler()
    CLI_handler.setLevel(logging.INFO)  # В консоли показываем только INFO и выше
    CLI_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("logs.log", encoding="utf-8")    #a - режим дозаписи (append)
    file_handler.setLevel(logging.DEBUG)  
    file_handler.setFormatter(formatter)

    logger.addHandler(CLI_handler)
    logger.addHandler(file_handler)

    return logger

logger = startLogging()