import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_PATH = Path.home() / "Documents" / "smart_rename_log.txt"

handler = RotatingFileHandler(str(LOG_PATH), maxBytes=8_000_000, backupCount=3, encoding='utf-8')
formatter = logging.Formatter("%(asctime)s\t%(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

logger = logging.getLogger("SmartRename")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
