# Week 3 — Web Automation (Partial)

Basic web scraping with `requests` and `BeautifulSoup`.

## What's here

| File | Purpose |
|------|---------|
| `first_scrape.py` | Fetch a page and extract basic info |
| `data/books.csv` | Sample output — 20 books from books.toscrape.com |

## What was skipped

The full Week 3 curriculum (sessions, cookies, Playwright, logins, ethics) was skipped in favor of moving directly to APIs (Week 4). The foundation here is enough to build scrapers for static pages.

## If you return to this

Recommended order:
1. **Sessions** — preserve cookies across requests
2. **Playwright** — handle JavaScript-rendered pages
3. **Rate limits + robots.txt** — scrape responsibly
4. **Hidden APIs** — find JSON endpoints in DevTools

## Legal note

Scraping is legal for public data within ToS. **Always check**:
- `robots.txt` — what the site allows
- Terms of Service — what you agreed to
- Rate limits — don't DoS small sites

When in doubt, look for an API first.
