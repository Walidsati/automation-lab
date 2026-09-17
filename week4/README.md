# Week 4 — APIs & Integrations

Talking to services the right way: REST, OAuth2, webhooks, and bots.

## What was built

| File | Purpose |
|------|---------|
| `first_api.py` | Call GitHub's public API (no auth) |
| `github_profile.py` | Fetch and summarize a user's repos |
| `auth_test.py` | Compare anonymous vs authenticated rate limits (60 vs 5,000/hour) |
| `my_private_info.py` | Fetch authenticated user data |
| `sheets_client.py` | Reusable Google Sheets client (OAuth2) |
| `read_sheet.py` | Read data from a Google Sheet |
| `write_sheet.py` | Compute summary + write back to Sheet |
| `webhook_server.py` | FastAPI webhook receiver with HMAC signature verification |
| `telegram_send.py` | Send Telegram messages via Bot API |
| `telegram_bot.py` | Full bot — receives commands, replies |
| `telegram_send_file.py` | Send files (PDFs) via Telegram |
| `cloud_bot.py` | Telegram bot running in GitHub Actions (no server needed) |

## Key concepts

- **REST** — GET/POST/PUT/DELETE, status codes, headers, JSON
- **API keys** — Bearer tokens in headers, `.env` + GitHub Secrets
- **OAuth2** — full flow: authorize → callback → tokens → refresh
- **Google APIs** — Sheets, Drive, Gmail via `google-api-python-client`
- **Webhooks** — receive HTTP from GitHub, verify with HMAC
- **Telegram bots** — polling and webhook modes
- **Cloud bots** — run agent in GitHub Actions, state in repo

## Rate limits

| API | Anonymous | Authenticated |
|-----|-----------|---------------|
| GitHub | 60/hour | 5,000/hour |

**Always authenticate when you can.**

## Webhook security

Signatures prove a request came from the claimed sender. `webhook_server.py` uses HMAC-SHA256 with a shared secret to verify GitHub webhooks. Unsigned requests → 401.

## The cloud bot pattern

`cloud_bot.py` runs in GitHub Actions on a schedule. It polls Telegram, processes commands, saves state in `bot_state.json`, and commits back to the repo. **No server, no tunnel, no VPS.** Just GitHub's free compute.

## Setup

Requires `.env` with:
