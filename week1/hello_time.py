#!/usr/bin/env python3
"""Logs the current date and time to a file next to this script."""

import logging
import sys
from datetime import datetime
from pathlib import Path

# The folder this script lives in — works on Mac, Linux, anywhere.
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "hello_time.log"


def setup_logging() -> logging.Logger:
    """Configure logging to file only (no terminal output needed in automation)."""

    logger = logging.getLogger("hello_time")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Also print to stdout so GitHub Actions logs show it
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
