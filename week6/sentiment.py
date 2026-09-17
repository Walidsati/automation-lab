#!/usr/bin/env python3
"""Classify sentiment of text — returns structured JSON."""

import json
import re

from ollama import chat

MODEL = "gemma4:e4b"

SYSTEM_PROMPT = """You are a sentiment analyzer. You MUST return valid JSON.

Required format:
{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": <number between 0.0 and 1.0>,
  "reason": "<string under 20 words>"
}

Do NOT wrap in markdown. Do NOT add prose. Output ONLY the JSON object."""


def extract_json(text: str) -> dict:
    """Try hard to extract valid JSON from LLM output."""
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

    raise ValueError(f"Could not extract JSON from: {text!r}")


def analyze(text: str, retries: int = 2) -> dict:
    """Return structured sentiment analysis with retries and safe parsing."""
    last_error = None

    for attempt in range(retries + 1):
        try:
            response = chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                format="json",
            )
            content = response["message"]["content"]
            result = extract_json(content)

            if result.get("sentiment") not in ("positive", "negative", "neutral"):
                raise ValueError(f"Invalid sentiment: {result.get('sentiment')}")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            if attempt < retries:
                print(f"  [retry {attempt + 1}] {e}")
                continue

    return {
        "sentiment": "unknown",
        "confidence": 0.0,
        "reason": f"Parsing failed: {last_error}",
    }


def main():
    samples = [
        "This product changed my life. Absolutely incredible.",
        "It's fine, does what it says, nothing special.",
        "Terrible. Broke after two days. Complete waste of money.",
        "The customer service was slow, but the product itself is great.",
    ]

    for text in samples:
        print(f"Text:      {text}")
        result = analyze(text)
        print(f"Sentiment: {result['sentiment']} ({result['confidence']:.2f})")
        print(f"Reason:    {result['reason']}")
        print()


if __name__ == "__main__":
    main()
