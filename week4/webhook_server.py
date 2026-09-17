#!/usr/bin/env python3
"""Webhook receiver with GitHub signature verification."""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode()

app = FastAPI()


def verify_signature(body: bytes, signature_header: str) -> bool:
    """Verify GitHub's HMAC signature against the raw body."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    received = signature_header.removeprefix("sha256=")
    expected = hmac.new(GITHUB_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
    # Constant-time comparison (prevents timing attacks)
    return hmac.compare_digest(received, expected)


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    event = request.headers.get("x-github-event", "unknown")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if not verify_signature(body, signature):
        print(f"\n[{now}] REJECTED — signature invalid (event={event})")
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body) if body else {}
    print(f"\n[{now}] ✓ Verified webhook: {event}")
    if event == "push":
        ref = payload.get("ref", "")
        pusher = payload.get("pusher", {}).get("name", "?")
        commits = payload.get("commits", [])
        print(f"  Ref:    {ref}")
        print(f"  Pusher: {pusher}")
        print(f"  Commits: {len(commits)}")
        for c in commits[:3]:
            print(f"    - {c['message']}")
    elif event == "ping":
        print(f"  Zen: {payload.get('zen', '')}")

    return {"received": True, "verified": True}
