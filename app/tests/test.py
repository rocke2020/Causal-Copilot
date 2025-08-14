from pathlib import Path

from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.add(
    Path(__file__).with_suffix(".log"), mode="w", encoding="utf-8", level="DEBUG"
)

import dask.array as da


def main():
    logger.info("end")


if __name__ == "__main__":
    main()
