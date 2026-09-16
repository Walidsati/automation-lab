#!/usr/bin/env python3
"""Compare anonymous vs authenticated GitHub API rate limits."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ["GITHUB_TOKEN"]


def check_auth(headers=None, label="anonymous"):
    response = httpx.get(
        "https://api.github.com/rate_limit",
        headers=headers or {},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    core = data["resources"]["core"]
    print(f"{label}:")
    print(f"  Limit:     {core['limit']}")
    print(f"  Remaining: {core['remaining']}")
    print()


def main():
    check_auth(label="anonymous")
    check_auth(
        headers={"Authorization": f"Bearer {TOKEN}"},
        label="authenticated",
    )


if __name__ == "__main__":
    main()
