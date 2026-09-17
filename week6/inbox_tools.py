#!/usr/bin/env python3
"""Tools for the inbox agent — actions it can take on emails."""

import json
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DRAFTS_DIR = SCRIPT_DIR / "drafts"
SPAM_DIR = SCRIPT_DIR / "spam"
TASKS_FILE = SCRIPT_DIR / "tasks" / "tasks.md"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def save_draft_reply(email_id: str, recipient: str, body: str) -> str:
    """Save a draft reply to drafts/<email_id>.txt"""
    DRAFTS_DIR.mkdir(exist_ok=True)
    path = DRAFTS_DIR / f"{email_id}.txt"
    content = f"To: {recipient}\nGenerated: {_now()}\n\n{body}\n"
    path.write_text(content)
    return f"Draft saved to {path.name}"


def flag_as_spam(email_id: str, source_path: str) -> str:
    """Move the source email file to the spam/ folder."""
    SPAM_DIR.mkdir(exist_ok=True)
    src = Path(source_path)
    if not src.exists():
        return f"Source not found: {source_path}"
    dst = SPAM_DIR / src.name
    src.rename(dst)
    return f"Moved {src.name} to spam/"


def add_to_task_list(email_id: str, task: str) -> str:
    """Append a task to tasks/tasks.md"""
    TASKS_FILE.parent.mkdir(exist_ok=True)
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("# Task List\n\n")
    line = f"- [ ] [{email_id}] {task}  _(added {_now()})_\n"
    with TASKS_FILE.open("a") as f:
        f.write(line)
    return f"Task added: {task[:60]}"


def archive_email(email_id: str, source_path: str) -> str:
    """Mark email as archived (moves to processed/)."""
    processed = SCRIPT_DIR / "processed"
    processed.mkdir(exist_ok=True)
    src = Path(source_path)
    if not src.exists():
        return f"Source not found: {source_path}"
    dst = processed / src.name
    src.rename(dst)
    return f"Archived {src.name}"


# ---- Registry for LLM tool calling ----
TOOL_REGISTRY = {
    "save_draft_reply": {
        "function": save_draft_reply,
        "description": "Save a draft reply for an email.",
        "parameters": {
            "email_id": {"type": "string", "description": "Email ID, e.g. 'email_001'"},
            "recipient": {"type": "string", "description": "Recipient email address"},
            "body": {"type": "string", "description": "Draft reply text"},
        },
    },
    "flag_as_spam": {
        "function": flag_as_spam,
        "description": "Flag an email as spam and move it to the spam folder.",
        "parameters": {
            "email_id": {"type": "string"},
            "source_path": {"type": "string", "description": "Path to the email file"},
        },
    },
    "add_to_task_list": {
        "function": add_to_task_list,
        "description": "Add an action item to the task list.",
        "parameters": {
            "email_id": {"type": "string"},
            "task": {"type": "string", "description": "The task description"},
        },
    },
    "archive_email": {
        "function": archive_email,
        "description": "Archive an email (move it to processed/).",
        "parameters": {
            "email_id": {"type": "string"},
            "source_path": {"type": "string"},
        },
    },
}


def get_tools_for_llm() -> list[dict]:
    tools = []
    for name, spec in TOOL_REGISTRY.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": spec["description"],
                "parameters": {
                    "type": "object",
                    "properties": spec["parameters"],
                    "required": list(spec["parameters"].keys()),
                },
            },
        })
    return tools


def call_tool(name: str, args: dict) -> str:
    if name not in TOOL_REGISTRY:
        return f"Unknown tool: {name}"
    try:
        return TOOL_REGISTRY[name]["function"](**args)
    except Exception as e:
        return f"Tool error: {e}"


if __name__ == "__main__":
    # Quick tests
    print(save_draft_reply("test", "a@b.com", "Hello world"))
    print(add_to_task_list("test", "Verify the thing"))
