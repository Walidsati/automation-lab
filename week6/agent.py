#!/usr/bin/env python3
"""A simple agent that can use tools to answer questions."""

import json

from ollama import chat

from tools import get_tools_for_llm, call_tool

MODEL = "gemma4:e4b"
MAX_ITERATIONS = 5


def run_agent(user_question: str, verbose: bool = True) -> str:
    """Run the agent loop until the model gives a final answer."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to tools. "
                "Use them when needed to answer questions accurately. "
                "If no tool is needed, answer directly."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    tools = get_tools_for_llm()

    for iteration in range(MAX_ITERATIONS):
        if verbose:
            print(f"\n[iteration {iteration + 1}]")

        response = chat(model=MODEL, messages=messages, tools=tools)
        message = response["message"]

        tool_calls = message.get("tool_calls") or []
        if tool_calls:
            messages.append(message)

            for tc in tool_calls:
                name = tc["function"]["name"]
                args = tc["function"]["arguments"]
                if isinstance(args, str):
                    args = json.loads(args)

                if verbose:
                    print(f"  → calling tool: {name}({args})")

                result = call_tool(name, args)

                if verbose:
                    preview = result[:100] + ("..." if len(result) > 100 else "")
                    print(f"  ← result: {preview}")

                messages.append({
                    "role": "tool",
                    "content": str(result),
                })
            continue

        return message["content"]

    return "Error: exceeded max iterations."


def main():
    questions = [
        "What is the current UTC time?",
        "Calculate 123 * 456 + 789.",
        "What does the top-level README.md say about the project?",
        "What is 2 + 2, and what time is it right now?",
    ]

    for q in questions:
        print(f"\n{'=' * 60}")
        print(f"USER: {q}")
        print("=" * 60)
        answer = run_agent(q)
        print(f"\nANSWER: {answer}")


if __name__ == "__main__":
    main()
