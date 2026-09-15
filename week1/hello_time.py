#!/usr/bin/env python3
"""Logs the current date and time. Chooses the log file based on environment."""

import time
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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
        datefmt="%Y-%m-%d %H:%M:%S UTC",
    )
    formatter.converter = time.gmtime

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
        utc_now = datetime.now(timezone.utc)
        beirut = utc_now.astimezone(ZoneInfo("Asia/Beirut"))

        logger.info(f"UTC now:    {utc_now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        logger.info(f"Beirut now: {beirut.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info("hello_time finished successfully")
        return 0
    except Exception:
        logger.exception("hello_time failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
