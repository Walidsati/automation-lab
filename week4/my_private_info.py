#!/usr/bin/env python3
"""Fetch authenticated user info — only visible with a token."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ["GITHUB_TOKEN"]


def main():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = httpx.get(
        "https://api.github.com/user",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    print(f"Login:              {data['login']}")
    print(f"Name:               {data.get('name')}")
    print(f"Email:              {data.get('email')}")
    print(f"Public repos:       {data['public_repos']}")
    print(f"Private repos:      {data.get('total_private_repos', 0)}")
    print(f"Owned private repos:{data.get('owned_private_repos', 0)}")
    print(f"Followers:          {data['followers']}")
    print(f"Following:          {data['following']}")
    print(f"Created at:         {data['created_at']}")


if __name__ == "__main__":
    main()
