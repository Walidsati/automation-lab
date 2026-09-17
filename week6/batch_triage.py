#!/usr/bin/env python3
"""Triage a batch of emails from JSON, save results."""

import json
from pathlib import Path

from email_triage import triage_email

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT = SCRIPT_DIR / "emails.json"
OUTPUT = SCRIPT_DIR / "triaged_results.json"


def main():
    emails = json.loads(INPUT.read_text())
    print(f"Loaded {len(emails)} emails\n")

    results = []
    for i, email in enumerate(emails, 1):
        print(f"[{i}/{len(emails)}] {email['subject'][:60]}")
        t = triage_email(email["sender"], email["subject"], email["body"])
        results.append({
            "sender": email["sender"],
            "subject": email["subject"],
            "triage": {
                "category": t.category,
                "priority": t.priority,
                "needs_reply": t.needs_reply,
                "summary": t.summary,
                "action_items": t.action_items,
                "draft_reply": t.draft_reply,
            },
        })
        print(f"  → {t.category} | {t.priority} | reply: {t.needs_reply}")

    OUTPUT.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {OUTPUT}")

    # Summary stats
    from collections import Counter
    cats = Counter(r["triage"]["category"] for r in results)
    prios = Counter(r["triage"]["priority"] for r in results)
    print(f"\nCategories: {dict(cats)}")
    print(f"Priorities: {dict(prios)}")


if __name__ == "__main__":
    main()
