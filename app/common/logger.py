import os
import logging
from datetime import datetime

LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILES = os.path.join(
    LOGS_DIR,
    f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
)

logging.basicConfig(
    filename=LOGS_DIR,
    format='%(asctime)s -%(levelname)s -%(message)s',
    level = logging.INFO
)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger