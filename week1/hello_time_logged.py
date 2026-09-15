#!/usr/bin/env python3
"""Logs the current date and time using Python's logging module."""

import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / "automation-lab" / "week1" / "hello_time.log"

def setup_logging() -> logging.Logger:
    """Configure logging to write to both file and terminal."""

    logger = logging.getLogger("hello_time")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if script runs twice in the same process
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler 1: write to file
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler 2: write to terminal (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

def main() -> int:
    logger = setup_logging()

    logger.info("hello_time started")


    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"current time: {now}")
        logger.info("hello_time finished successfully")
        return 0
    except Exception:
        logger.exception("hello_time failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
