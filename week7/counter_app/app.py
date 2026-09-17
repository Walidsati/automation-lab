#!/usr/bin/env python3
"""Tiny FastAPI app with a Redis-backed counter."""

import os
import socket

import redis
from fastapi import FastAPI

app = FastAPI(title="Counter API")

# Read Redis host from env (default: "redis" — the service name in compose)
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.get("/")
def root():
    return {
        "service": "counter-api",
        "hostname": socket.gethostname(),
        "redis_host": REDIS_HOST,
    }


@app.get("/increment")
def increment():
    count = r.incr("counter")
    return {"counter": count}


@app.get("/current")
def current():
    count = r.get("counter") or "0"
    return {"counter": int(count)}


@app.get("/health")
def health():
    """Health check — verify Redis is reachable."""
    try:
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
