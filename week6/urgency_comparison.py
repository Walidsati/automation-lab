#!/usr/bin/env python3
"""Compare plain-code vs LLM urgency detection."""

from email_triage import triage_email

# ---- Approach A: plain code ----
URGENT_KEYWORDS = ["urgent", "asap", "immediately", "critical", "deadline", "today"]


def is_urgent_plain(subject: str, body: str) -> bool:
    text = (subject + " " + body).lower()
    return any(kw in text for kw in URGENT_KEYWORDS)


# ---- Approach B: LLM ----
def is_urgent_llm(subject: str, body: str) -> bool:
    t = triage_email("test@example.com", subject, body)
    return t.priority == "urgent"


# ---- Test cases ----
CASES = [
    {
        "subject": "URGENT: contract review needed by EOD",
        "body": "Please review and send feedback today.",
        "expected": True,
    },
    {
        "subject": "Question about pricing",
        "body": "Hi, no rush but can you send me the price list when you have a moment?",
        "expected": False,
    },
    {
        "subject": "Just a heads up",
        "body": "FYI — the meeting next week is at 3pm, not 2pm. No action needed.",
        "expected": False,
    },
    {
        "subject": "Server down — clients affected",
        "body": "Our production server is unreachable. Customers are complaining. Need help ASAP.",
        "expected": True,
    },
    {
        "subject": "Contract deadline",
        "body": "Just a reminder that the contract clause we discussed needs review, but we have until next Friday.",
        "expected": False,   # ambiguous — "deadline" keyword but not actually urgent
    },
]


def main():
    print(f"{'Expected':<10} {'Plain code':<12} {'LLM':<8} {'Subject'}")
    print("-" * 80)

    plain_correct = 0
    llm_correct = 0

    for case in CASES:
        expected = case["expected"]
        plain = is_urgent_plain(case["subject"], case["body"])
        llm = is_urgent_llm(case["subject"], case["body"])

        p_mark = "✅" if plain == expected else "❌"
        l_mark = "✅" if llm == expected else "❌"

        if plain == expected:
            plain_correct += 1
        if llm == expected:
            llm_correct += 1

        print(f"{str(expected):<10} {p_mark} {str(plain):<9} {l_mark} {str(llm):<6} {case['subject'][:40]}")

    print("-" * 80)
    print(f"Plain code correct: {plain_correct}/{len(CASES)}")
    print(f"LLM correct:        {llm_correct}/{len(CASES)}")


if __name__ == "__main__":
    main()
