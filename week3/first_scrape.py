#!/usr/bin/env python3
"""Fetch the books.toscrape.com homepage and print basic info."""

import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/"


def main():
    # Step 1 — fetch
    response = requests.get(URL, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)} chars")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    # Step 2 — parse
    soup = BeautifulSoup(response.content, "lxml")

    # Page title
    print(f"\nPage title: {soup.title.string.strip}")

    # Count books on the page
    books = soup.find_all("article", class_="product_pod")
    print(f"Books on page: {len(books)}")

    # Show the first book's details
    first = books[0]
    title = first.find("h3").find("a")["title"]
    price = first.find("p", class_="price_color").string
    print(f"\nFirst book:")
    print(f"  Title: {title}")
    print(f"  Price: {price}")


if __name__ == "__main__":
    main()
