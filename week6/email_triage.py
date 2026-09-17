#!/usr/bin/env python3
"""Classify, summarize, and draft replies for emails."""

import json
import re
from dataclasses import dataclass

from ollama import chat

MODEL = "gemma4:e4b"

SYSTEM_PROMPT = """You are an email triage assistant. Analyze the email and return JSON with these exact fields:

{
  "category": one of "customer_support", "sales", "spam", "personal", "newsletter", "system_notification", "other",
  "priority": one of "urgent", "normal", "low",
  "needs_reply": true or false,
  "summary": "one sentence summary (under 25 words)",
  "action_items": ["short action 1", "short action 2"],
  "draft_reply": "a polite, brief reply (under 60 words) or null if no reply needed"
}

Rules:
- Be concise
- action_items should be empty [] if none
- draft_reply should be null if needs_reply is false
- Match the tone of the sender
- Use "system_notification" for automated alerts from services (CI failures, monitoring, etc.)

Do NOT wrap in markdown. Output ONLY the JSON object."""


@dataclass
class Triage:
    category: str
    priority: str
    needs_reply: bool
    summary: str
    action_items: list[str]
    draft_reply: str | None


def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not extract JSON: {text!r}")


def triage_email(sender: str, subject: str, body: str) -> Triage:
    """Analyze an email and return structured triage."""

    email_text = f"From: {sender}\nSubject: {subject}\n\n{body}"

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text},
        ],
        format="json",
    )

    data = extract_json(response["message"]["content"])

    return Triage(
        category=data.get("category", "other"),
        priority=data.get("priority", "normal"),
        needs_reply=bool(data.get("needs_reply", False)),
        summary=data.get("summary", ""),
        action_items=data.get("action_items", []),
        draft_reply=data.get("draft_reply"),
    )


# ---- Demo emails ----
SAMPLES = [
    {
        "sender": "customer@example.com",
        "subject": "Refund request — order #12345",
        "body": (
            "Hi, I ordered a widget last week and it arrived broken. "
            "I'd like a full refund please. Order number is 12345. "
            "Thanks, Maria"
        ),
    },
    {
        "sender": "newsletter@techcrunch.com",
        "subject": "Weekly roundup: AI funding hits new highs",
        "body": (
            "This week in tech: AI startups raised $2B, OpenAI announces... "
            "(unsubscribe link at bottom)"
        ),
    },
    {
        "sender": "boss@mycompany.com",
        "subject": "URGENT: contract review needed by EOD",
        "body": (
            "Hi, I need you to review the attached contract for the Acme deal "
            "and send feedback before 5 PM today. This is time-sensitive. Thanks."
        ),
    },
    {
        "sender": "prince@nigeria-oil.com",
        "subject": "CONFIDENTIAL BUSINESS PROPOSAL",
        "body": (
            "Dear friend, I am the son of a wealthy oil minister. "
            "I have $45 million USD to transfer to your account..."
        ),
    },
]


def main():
    for i, email in enumerate(SAMPLES, 1):
        print(f"\n{'=' * 70}")
        print(f"EMAIL {i}: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"{'=' * 70}")

        t = triage_email(email["sender"], email["subject"], email["body"])

        print(f"Category:      {t.category}")
        print(f"Priority:      {t.priority}")
        print(f"Needs reply:   {t.needs_reply}")
        print(f"Summary:       {t.summary}")
        if t.action_items:
            print("Action items:")
            for item in t.action_items:
                print(f"  • {item}")
        if t.draft_reply:
            print(f"\nDraft reply:\n{t.draft_reply}")


if __name__ == "__main__":
    main()
