# Automation Lab

Personal automation course — 8 weeks, from zero to a full automation stack.

Every project runs in two places: locally on macOS (via launchd) and in the cloud (via GitHub Actions). Both are version-controlled, logged, and self-committing.

## Structure

    automation-lab/
    ├── week1/   # Make scripts run themselves: launchd + GitHub Actions
    ├── week2/   # Data & documents: pandas, Excel, PDFs, email
    ├── week3/   # Web automation: requests, BeautifulSoup, Playwright
    ├── week4/   # APIs & integrations: OAuth, Google APIs, Telegram
    ├── week5/   # No-code + GitHub Actions deep dive
    ├── week6/   # AI automation: LLMs, function calling, agents
    ├── week7/   # DevOps: Docker, CI/CD, deployment
    └── week8/   # Capstone: personal automation stack

## Week 1 — Make scripts run themselves

- hello_time.py — logs the current time, detects runner (Mac vs cloud)
- launchd/com.walid.hellotime.plist — macOS scheduled job (daily 9 AM)
- .github/workflows/hello.yml — GitHub Actions workflow (daily 6 AM UTC)
- Auto-commits cloud output back to the repo

Logs:
- week1/hello_time_local.log — written by macOS launchd
- week1/hello_time_cloud.log — written by GitHub Actions
