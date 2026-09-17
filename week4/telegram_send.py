#!/usr/bin/env python3
"""Send a Telegram message via the Bot API."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_message(text: str) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = httpx.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    result = send_message("Hello from Python! 🐍")
    print(f"Sent: message_id={result['result']['message_id']}")


if __name__ == "__main__":
    main()
