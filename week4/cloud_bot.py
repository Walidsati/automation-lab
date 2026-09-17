#!/usr/bin/env python3
"""Telegram bot that runs in GitHub Actions — polls once and exits."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = Path(__file__).resolve().parent / "bot_state.json"
load_dotenv(ROOT / ".env")

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
API = f"https://api.telegram.org/bot{TOKEN}"


def send_message(text: str) -> None:
    httpx.post(
        f"{API}/sendMessage",
        json={"chat_id": ALLOWED_CHAT_ID, "text": text},
        timeout=10,
    )


def get_updates(offset: int | None = None) -> list[dict]:
    params = {"timeout": 5}
    if offset is not None:
        params["offset"] = offset
    r = httpx.get(f"{API}/getUpdates", params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("result", [])


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_update_id": 0}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def run_report() -> tuple[bool, str]:
    """Run week2/run_report.py and return (success, message)."""
    script = ROOT / "week2" / "run_report.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode == 0:
            return True, "✅ Report generated and emailed."
        else:
            return False, f"❌ Report failed:\n{result.stderr[-500:]}"
    except subprocess.TimeoutExpired:
        return False, "❌ Report timed out after 3 minutes."
    except Exception as e:
        return False, f"❌ Error: {e}"


def handle(text: str) -> None:
    text = text.strip().lower()

    if text.startswith("/start") or text.startswith("/help"):
        send_message(
            "🤖 Cloud bot online.\n\n"
            "Commands:\n"
            "/status — check if alive\n"
            "/time — current UTC\n"
            "/report — generate and email sales report\n"
            "/help — this menu"
        )
    elif text.startswith("/status"):
        send_message("✅ Cloud bot is alive (GitHub Actions).")
    elif text.startswith("/time"):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        send_message(f"🕐 {now}")
    elif text.startswith("/report"):
        send_message("⏳ Generating report...")
        ok, msg = run_report()
        send_message(msg)
    else:
        send_message(f"Unknown command: {text}\nSend /help")


def main():
    state = load_state()
    offset = state.get("last_update_id", 0) + 1 if state.get("last_update_id") else None

    try:
        updates = get_updates(offset=offset)
    except Exception as e:
        print(f"Failed to fetch updates: {e}")
        return

    if not updates:
        print("No new updates.")
        return

    print(f"Processing {len(updates)} update(s).")

    for update in updates:
        # Advance state even if we ignore the message
        state["last_update_id"] = update["update_id"]

        msg = update.get("message")
        if not msg:
            continue

        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        sender = msg.get("from", {}).get("first_name", "?")

        # Security: only respond to the allowed chat
        if chat_id != ALLOWED_CHAT_ID:
            print(f"Ignoring message from unauthorized chat {chat_id}")
            continue

        print(f"[{sender}] {text}")
        handle(text)

    save_state(state)
    print(f"Saved state: last_update_id={state['last_update_id']}")


if __name__ == "__main__":
    main()
