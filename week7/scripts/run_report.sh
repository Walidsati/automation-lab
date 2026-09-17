#!/usr/bin/env bash
#
# run_report.sh — wrapper that runs the Week 2 report pipeline.
#
# Usage: ./run_report.sh
#
# Exit codes:
#   0 — success
#   1 — venv not activated / missing files
#   2 — report script failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
REPORT_SCRIPT="$REPO_ROOT/week2/run_report.py"
LOG_FILE="$SCRIPT_DIR/run_report.log"

if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; NC=''
fi

log() {
  local level="$1"
  local message="$2"
  local ts
  ts="$(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  echo -e "${ts} [${level}] ${message}" | tee -a "$LOG_FILE"
}

preflight() {
  log "INFO" "Starting preflight checks"

  if [ ! -f "$REPORT_SCRIPT" ]; then
    log "ERROR" "Report script not found: $REPORT_SCRIPT"
    exit 1
  fi

  if [ -z "${VIRTUAL_ENV:-}" ]; then
    log "ERROR" "No virtual environment active. Run: source .venv/bin/activate"
    exit 1
  fi

  log "INFO" "Using Python: $(which python)"
  log "INFO" "Preflight passed"
}

main() {
  preflight
  log "INFO" "Report pipeline starting"

  log "INFO" "Running report: $REPORT_SCRIPT"
  python "$REPORT_SCRIPT"
  log "INFO" "Report succeeded"

  log "INFO" "Pipeline complete"
  return 0
}

main "$@"
