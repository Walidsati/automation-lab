#!/usr/bin/env python3
"""Call the GitHub public API — no auth needed."""

import httpx



def main():
    url = "https://api.github.com/users/Walidsati"

    # Make the request
    response = httpx.get(url, timeout=10)

    # Check status
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    # Parse JSON
    data = response.json()

    # Show some fields
    print(f"\nGitHub user: {data['login']}")
    print(f"Name: {data.get('name')}")
    print(f"Public repos: {data['public_repos']}")
    print(f"Followers: {data['followers']}")
    print(f"Created at: {data['created_at']}")

    # Rate limit info (GitHub tells us in headers)
    print(f"\nRate limit:")
    print(f"  Limit:     {response.headers.get('x-ratelimit-limit')}")
    print(f"  Remaining: {response.headers.get('x-ratelimit-remaining')}")
    print(f"  Resets at: {response.headers.get('x-ratelimit-reset')}")


if __name__ == "__main__":
    main()
