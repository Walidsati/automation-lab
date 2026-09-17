#!/usr/bin/env python3
"""AI agent that processes an inbox and takes actions."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ollama import chat

from inbox_tools import get_tools_for_llm, call_tool

SCRIPT_DIR = Path(__file__).resolve().parent
INBOX_DIR = SCRIPT_DIR / "inbox"
MODEL = "gemma4:e4b"
MAX_ITERATIONS = 6


SYSTEM_PROMPT = """You are an inbox triage agent. For each email, you must:

1. Analyze the email: category, priority, whether it needs a reply
2. Take appropriate actions using the tools available:
   - Use `save_draft_reply` for emails that need a reply (write a concise, polite reply)
   - Use `add_to_task_list` for any action items you identify
   - Use `flag_as_spam` for spam/phishing emails
   - Use `archive_email` for emails that don't need a reply and aren't spam

Guidelines:
- Spam (phishing, scams) → flag_as_spam only, no draft
- Newsletters, notifications → archive_email only
- Emails needing a reply → save_draft_reply + add_to_task_list
- Urgent emails → save_draft_reply + add_to_task_list

Always take at least one action per email. Be decisive."""


def parse_email_file(path: Path) -> dict:
    """Parse a simple text email file."""
    text = path.read_text()
    lines = text.split("\n")
    sender = subject = ""
    body_lines = []
    in_body = False

    for line in lines:
        if line.startswith("From:"):
            sender = line[5:].strip()
        elif line.startswith("Subject:"):
            subject = line[8:].strip()
        elif line.startswith("Date:"):
            continue
        elif line.strip() == "" and not in_body:
            in_body = True
        elif in_body:
            body_lines.append(line)

    return {
        "id": path.stem,
        "path": str(path),
        "sender": sender,
        "subject": subject,
        "body": "\n".join(body_lines).strip(),
    }


def run_agent_for_email(email: dict) -> list[str]:
    """Run the agent loop for one email; return list of tool actions taken."""
    actions = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Email ID: {email['id']}\n"
                f"File: {email['path']}\n"
                f"From: {email['sender']}\n"
                f"Subject: {email['subject']}\n\n"
                f"{email['body']}"
            ),
        },
    ]

    tools = get_tools_for_llm()

    for iteration in range(MAX_ITERATIONS):
        response = chat(model=MODEL, messages=messages, tools=tools)
        message = response["message"]

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            # No tools called → agent has nothing more to do
            return actions

        messages.append(message)

        for tc in tool_calls:
            name = tc["function"]["name"]
            args = tc["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)

            result = call_tool(name, args)
            actions.append(f"{name}({list(args.keys())}) → {result}")

            messages.append({
                "role": "tool",
                "content": str(result),
            })

    return actions + ["[max iterations reached]"]


def main():
    # Snapshot inbox before processing
    inbox_files = sorted(INBOX_DIR.glob("*.txt"))
    total = len(inbox_files)
    print(f"Processing {total} emails from {INBOX_DIR}\n")

    # Process each email
    results = []
    for i, path in enumerate(inbox_files, 1):
        email = parse_email_file(path)
        print(f"[{i}/{total}] {email['subject'][:50]}")

        actions = run_agent_for_email(email)
        for a in actions:
            print(f"     → {a}")
        print()

        results.append({
            "id": email["id"],
            "subject": email["subject"],
            "sender": email["sender"],
            "actions": actions,
        })

    # Write summary
    summary_path = SCRIPT_DIR / "summary_report.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Inbox Summary — {now}\n", f"Processed **{total}** emails.\n"]
    for r in results:
        lines.append(f"## {r['id']}: {r['subject']}")
        lines.append(f"**From:** {r['sender']}\n")
        for a in r["actions"]:
            lines.append(f"- {a}")
        lines.append("")
    summary_path.write_text("\n".join(lines))

    print(f"Summary written: {summary_path}")


if __name__ == "__main__":
    main()
