# Week 6 — AI Automation

Local LLM integration using **Ollama** (no API keys, private, free).

## What was built

| File | Purpose |
|------|---------|
| `first_chat.py` | First LLM interaction — a single chat call |
| `multi_turn.py` | Demonstrates stateless nature of LLMs (send history each call) |
| `sentiment.py` | Structured output — sentiment analysis with JSON schema + retries |
| `batch_sentiment.py` | Batch processing CSV → LLM → CSV |
| `tools.py` | Reusable tool definitions for function calling |
| `agent.py` | First agent loop — LLM chooses tools to answer questions |
| `email_triage.py` | Classify, summarize, and draft replies for emails |
| `batch_triage.py` | Batch process a JSON list of emails |
| `urgency_comparison.py` | Empirical comparison: plain code vs LLM |
| `rag_index.py` | Build a semantic search index of the repo |
| `rag_query.py` | Query the RAG index with natural language |
| `inbox_agent.py` | **Final project** — AI agent that takes actions on emails |
| `inbox_tools.py` | Tools the inbox agent can call |

## Models used

| Model | Size | Purpose |
|-------|------|---------|
| `gemma4:e4b` | 9.6 GB | Chat / reasoning |
| `nomic-embed-text` | 274 MB | Embeddings (for RAG) |

Both run **locally** on Apple Silicon via Ollama. No external API calls.

## The pipeline for `inbox_agent.py`

