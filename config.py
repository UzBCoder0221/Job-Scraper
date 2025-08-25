import os
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv(os.path.join(Path(__file__).resolve().parent,'.env'))

DJANGO_API_BASE= os.getenv('DJANGO_API_BASE')
BOT_API_TOKEN=os.getenv('BOT_API_TOKEN')

class ErrorLogger:
    os.makedirs('logs',exist_ok=True)
    def __init__(self) -> None:
        pass
    def getLogger(self):
        logger = logging.getLogger('bot_error_logger')
        logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler('logs/bot_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(error_handler)
        return logger