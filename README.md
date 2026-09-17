# Automation Lab

A personal automation stack built over 8 weeks, using Python, GitHub Actions, n8n, and various APIs.

Everything is version-controlled, cloud-scheduled, and self-documenting.

## What's in here

| Week | Theme | Key Deliverables |
|------|-------|------------------|
| [Week 1](week1/) | Make scripts run themselves | `launchd` + GitHub Actions, logging, secrets |
| [Week 2](week2/) | Data & documents | pandas → Excel → PDF → email pipeline |
| [Week 3](week3/) | Web automation | requests + BeautifulSoup basics |
| [Week 4](week4/) | APIs & integrations | OAuth2, Google Sheets, webhooks, Telegram bots |
| [Week 5](week5/) | No-code + CI/CD | n8n workflows, webhook integration, matrix builds |

## The system in motion

**Every day at 6 AM UTC (cloud, no laptop needed):**

1. GitHub Actions generates a sales report (Excel + PDF)
2. Emails it via Gmail
3. Commits the output back to the repo
4. Push triggers a GitHub webhook
5. Cloudflare tunnel forwards to local n8n
6. n8n filters (only report commits trigger)
7. Rich Telegram notification arrives on my phone

**Three tools, one coordinated pipeline, zero servers.**

## Stack

- **Python 3.12** — data processing, PDF generation, API clients
- **pandas, matplotlib, reportlab, xlsxwriter** — data & report tooling
- **GitHub Actions** — scheduled cloud execution, CI/CD
- **n8n** — visual workflow automation
- **Cloudflare Tunnels** — expose local services to the internet
- **Telegram Bot API** — real-time notifications & control
- **Google Sheets API** — OAuth2-based data integration
- **Docker** — reproducible environments

## Quick start

```bash
# Clone
git clone https://github.com/Walidsati/automation-lab.git
cd automation-lab

# Set up Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure secrets (create .env)
cp .env.example .env
# Fill in your credentials

