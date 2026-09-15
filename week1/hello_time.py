#!/usr/bin/env python3
"""Logs the current date and time. Chooses the log file based on environment."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Where this script lives
SCRIPT_DIR = Path(__file__).resolve().parent

# Pick file based on where we're running
if os.environ.get("GITHUB_ACTIONS") == "true":
    LOG_FILE = SCRIPT_DIR / "hello_time_cloud.log"
    RUNNER = "github-actions"
else:
    LOG_FILE = SCRIPT_DIR / "hello_time_local.log"
    RUNNER = "mac-launchd"


def setup_logging() -> logging.Logger:
    """Configure logging to file + terminal."""

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

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def main() -> int:
    logger = setup_logging()

    logger.info(f"hello_time started (runner={RUNNER})")
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
