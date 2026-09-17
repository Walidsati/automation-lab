#!/usr/bin/env python3
"""Simple script to run in Docker."""

import os
import sys
from datetime import datetime, timezone


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"Hello from Docker!")
    print(f"Current time: {now}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Environment: {os.environ.get('APP_ENV', 'default')}")
    print(f"Container hostname: {os.uname().nodename}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
