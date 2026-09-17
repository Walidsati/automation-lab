#!/usr/bin/env python3
"""Your first conversation with a local LLM."""

from ollama import chat

MODEL = "gemma4:e4b"


def main():
    messages = [
        {
            "role": "system",
            "content": "You are a concise assistant. Keep answers under 30 words.",
        },
        {
            "role": "user",
            "content": "What is automation, in simple terms?",
        },
    ]

    print(f"Model: {MODEL}")
    print(f"User:  {messages[-1]['content']}")
    print()

    response = chat(model=MODEL, messages=messages)
    reply = response["message"]["content"]

    print(f"Assistant: {reply}")
    print()
    print(f"[tokens: prompt={response.get('prompt_eval_count', '?')}, "
          f"completion={response.get('eval_count', '?')}]")


if __name__ == "__main__":
    main()
