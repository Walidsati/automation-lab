#!/usr/bin/env bash
#
# health_check.sh — check if a service is responding.
#
# Usage:
#   ./health_check.sh [URL]
#
# Exit:
#   0 — healthy
#   1 — unhealthy / unreachable

set -euo pipefail

URL="${1:-http://localhost:8000/health}"
TIMEOUT=5

response="$(curl -s -m "$TIMEOUT" "$URL" 2>&1 || true)"

if [ -z "$response" ]; then
  echo "❌ No response from $URL"
  exit 1
fi

# Parse JSON without needing jq — use Python
status="$(echo "$response" | python -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "parse_error")"

if [ "$status" = "healthy" ]; then
  echo "✅ $URL is healthy"
  exit 0
else
  echo "❌ $URL returned: $response"
  exit 1
fi

