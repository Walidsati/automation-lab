#!/usr/bin/env python3
"""Minimal webhook receiver."""

import json
from datetime import datetime, timezone

from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "message": "Webhook receiver is running"}


@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.body()
    payload = json.loads(body) if body else {}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n[{now}] Webhook received")
    print(f"Headers: {dict(request.headers)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    return {"received": True}

