#!/usr/bin/env python3
"""Ask questions against the RAG index."""

import json
import math
from pathlib import Path

import ollama

SCRIPT_DIR = Path(__file__).resolve().parent
INDEX_FILE = SCRIPT_DIR / "rag_index.json"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "gemma4:e4b"
TOP_K = 3


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def load_index() -> list[dict]:
    return json.loads(INDEX_FILE.read_text())


def search(question: str, index: list[dict], k: int = TOP_K) -> list[dict]:
    """Return top-k most relevant chunks for the question."""
    q_embed = ollama.embeddings(model=EMBED_MODEL, prompt=question)["embedding"]

    scored = []
    for entry in index:
        score = cosine_similarity(q_embed, entry["embedding"])
        scored.append({"score": score, "entry": entry})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]


def ask(question: str) -> str:
    """Retrieve + generate answer."""
    index = load_index()
    results = search(question, index)

    print(f"\nTop {len(results)} chunks:")
    for r in results:
        print(f"  [{r['score']:.3f}] {r['entry']['file']} (chunk {r['entry']['chunk_id']})")

    context = "\n\n---\n\n".join(
        f"[Source: {r['entry']['file']}]\n{r['entry']['text']}"
        for r in results
    )

    prompt = f"""You are answering questions about a GitHub repository.

Use ONLY the context below to answer. If the answer isn't in the context, say so.

CONTEXT:
{context}

QUESTION: {question}

Answer:"""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def main():
    questions = [
        "What did I learn about webhooks?",
        "How does the email triage system work?",
        "What is the daily report pipeline?",
        "What tools are used to generate PDF reports?",
    ]

    for q in questions:
        print(f"\n{'=' * 70}")
        print(f"Q: {q}")
        print("=" * 70)
        answer = ask(q)
        print(f"\nA: {answer}")


if __name__ == "__main__":
    main()
