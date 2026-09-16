#!/usr/bin/env python3
"""Fetch all repos for a GitHub user and summarize."""

from collections import Counter

import httpx

USERNAME = "Walidsati"
URL = f"https://api.github.com/users/{USERNAME}/repos"

def main():
    response = httpx.get(URL, timeout=10)
    response.raise_for_status()
    repos = response.json()
    print(f"Fetched {len(repos)} repos for {USERNAME}\n")

    for r in repos:
        name = r["name"]
        lang = r.get("language") or "—"
        stars = r["stargazers_count"]
        updated = r["updated_at"][:10]   # first 10 chars = YYYY-MM-DD
        print(f"  {name:30} {lang:12} ★{stars:3}  {updated}")

    print(f"\nSummary:")
    print(f"  Total repos: {len(repos)}")
    print(f"  Total stars: {sum(r['stargazers_count'] for r in repos)}")

    # Most common languages
    languages = Counter(r["language"] for r in repos if r["language"])
    if languages:
        print(f"  Languages:")
        for lang, count in languages.most_common():
            print(f"    {lang}: {count}")
    else:
        print(f"  Languages: (none)")


if __name__ == "__main__":
    main()
