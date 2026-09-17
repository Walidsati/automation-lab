#!/usr/bin/env python3
"""Build a searchable index of repo files using embeddings."""

import json
import math
from pathlib import Path

import ollama

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
INDEX_FILE = SCRIPT_DIR / "rag_index.json"
EMBED_MODEL = "nomic-embed-text"

# What to index — markdown and Python files, skip large/binary
INCLUDE_GLOBS = ["**/*.md", "**/*.py"]
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".github/actions"}

CHUNK_SIZE = 800       # characters per chunk
CHUNK_OVERLAP = 100    # overlap between chunks


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts) or path.name.startswith(".")


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks


def collect_files() -> list[Path]:
    files = []
    for pattern in INCLUDE_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            if not should_skip(path) and path.is_file():
                files.append(path)
    return sorted(set(files))


def main():
    files = collect_files()
    print(f"Found {len(files)} files to index\n")

    entries = []
    for i, path in enumerate(files, 1):
        rel = path.relative_to(REPO_ROOT)
        try:
            text = path.read_text(errors="ignore")
        except Exception as e:
            print(f"  [{i}/{len(files)}] SKIP {rel}: {e}")
            continue

        if len(text) < 50:
            continue  # too small

        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for j, chunk in enumerate(chunks):
            entries.append({
                "file": str(rel),
                "chunk_id": j,
                "text": chunk,
                # Placeholder — will be filled next loop
            })
        print(f"  [{i}/{len(files)}] {rel}: {len(chunks)} chunks")

    print(f"\nEmbedding {len(entries)} chunks...")
    for i, entry in enumerate(entries, 1):
        response = ollama.embeddings(model=EMBED_MODEL, prompt=entry["text"])
        entry["embedding"] = response["embedding"]
        if i % 20 == 0:
            print(f"  embedded {i}/{len(entries)}")

    INDEX_FILE.write_text(json.dumps(entries))
    print(f"\nSaved index: {INDEX_FILE}")
    print(f"Total chunks: {len(entries)}")


if __name__ == "__main__":
    main()
