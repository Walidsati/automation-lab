#!/usr/bin/env python3
"""Polling-based Telegram bot — responds to commands."""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id: int, text: str) -> None:
    """Send a message to a specific chat."""
    httpx.post(
        f"{API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )


def get_updates(offset: int | None = None) -> list[dict]:
    """Fetch new updates from Telegram."""
    params = {"timeout": 25}  # long-polling: wait up to 25s for a message
    if offset is not None:
        params["offset"] = offset
    r = httpx.get(f"{API}/getUpdates", params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("result", [])


def handle_command(chat_id: int, text: str) -> None:
    """Respond to a message. Add new commands here."""
    text = text.strip()

    if text.startswith("/start"):
        send_message(chat_id,
            "👋 Automation bot online.\n\n"
            "Commands:\n"
            "/hello — greeting\n"
            "/time — current UTC time\n"
            "/status — check if bot is alive"
        )
    elif text.startswith("/hello"):
        send_message(chat_id, "Hello Walid! 👋 Ready to automate.")
    elif text.startswith("/time"):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        send_message(chat_id, f"🕐 {now}")
    elif text.startswith("/status"):
        send_message(chat_id, "✅ Bot is running on your Mac.")
    else:
        send_message(chat_id, f"Unknown command: {text}\nTry /start")


def main():
    print("Bot started. Press Ctrl+C to stop.")
    print("Open Telegram and send /start to your bot.\n")

    # Skip old updates so we don't re-process history
    updates = get_updates()
    offset = updates[-1]["update_id"] + 1 if updates else None

    while True:
        try:
            updates = get_updates(offset=offset)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                who = msg.get("from", {}).get("first_name", "?")
                print(f"[{who}] {text}")
                handle_command(chat_id, text)
        except KeyboardInterrupt:
            print("\nStopping bot.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
