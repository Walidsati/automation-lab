#!/usr/bin/env python3
"""Send a document (PDF) to your Telegram chat."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
PDF = ROOT / "week2" / "data" / "sales_report.pdf"

url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

with PDF.open("rb") as f:
    files = {"document": (PDF.name, f, "application/pdf")}
    data = {"chat_id": CHAT_ID, "caption": "📊 Weekly sales report"}
    r = httpx.post(url, data=data, files=files, timeout=30)

print(f"Status: {r.status_code}")
print(f"Response: {r.json().get('ok')}")
