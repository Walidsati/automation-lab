#!/usr/bin/env python3
"""Multi-turn conversation — demonstrates stateless nature of LLMs."""

from ollama import chat

MODEL = "gemma4:e4b"


def ask(messages, question):
    """Add user question, get reply, append both to history."""
    messages.append({"role": "user", "content": question})
    response = chat(model=MODEL, messages=messages)
    reply = response["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    return reply


def main():
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Be concise."}
    ]

    # First question — establishes a topic
    q1 = "My favorite color is blue."
    a1 = ask(messages, q1)
    print(f"User:  {q1}")
    print(f"Bot:   {a1}\n")

    # Second question — refers back to the first
    q2 = "What's my favorite color?"
    a2 = ask(messages, q2)
    print(f"User:  {q2}")
    print(f"Bot:   {a2}\n")

    # Third question — again refers back
    q3 = "Suggest a shirt color that matches it."
    a3 = ask(messages, q3)
    print(f"User:  {q3}")
    print(f"Bot:   {a3}\n")

    print(f"Total messages in context: {len(messages)}")


if __name__ == "__main__":
    main()
