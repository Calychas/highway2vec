import logging
from datetime import datetime

from src.settings import *


def get_logger(name: str, logging_level: int = logging.WARNING) -> logging.Logger:
    logging.basicConfig(
        handlers=[
            logging.FileHandler(LOGS_DIR / datetime.now().strftime('logfile_%Y-%m-%d_%H-%M-%S.log')),
            logging.StreamHandler()
        ],
        format='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        level=logging_level
    )
    return logging.getLogger(name)
