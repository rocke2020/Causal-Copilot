from pathlib import Path

from dotenv import load_dotenv
from utils.logger import logger, set_log_level, LogLevel

load_dotenv()
set_log_level(LogLevel.DEBUG)

logger.info(f"starts {Path(__file__).name = }")