#!/usr/bin/env python3
"""Logs the current date and time to a file."""

from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / "automation-lab" / "week1" / "hello_time.log"

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] hello from launchd\n"

    with LOG_FILE.open("a") as f:
        f.write(line)

    print(line.strip())

if __name__ == "__main__":
    main()
