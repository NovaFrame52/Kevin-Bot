#!/usr/bin/env bash
set -euo pipefail

# Show Kevin Bot status and latest log
# Usage: kevin-status.sh [-t|--tail N] [-v|--verbose]

TAIL=0
VERBOSE=0
while [ $# -gt 0 ]; do
  case "$1" in
    -t|--tail)
      TAIL=${2:-0}
      shift 2 || true
      ;;
    -v|--verbose) VERBOSE=1; shift ;;
    -h|--help) echo "Usage: $0 [-t|--tail N] [-v|--verbose]"; exit 0 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# Resolve script/project root and load kevin.env to get KEVIN_DESKTOP_PATH
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load kevin.env if present to get KEVIN_DESKTOP_PATH
if [ -f "$PROJECT_ROOT/kevin.env" ]; then
  # shellcheck disable=SC1091
  set -a
  . "$PROJECT_ROOT/kevin.env"
  set +a
fi

if [ -n "${KEVIN_DESKTOP_PATH:-}" ]; then
  DESKTOP_PATH="$(eval echo \"$KEVIN_DESKTOP_PATH\")"
else
  DESKTOP_PATH="$HOME/Desktop"
fi

# Check running processes
PIDS=$(pgrep -f "Kevin_Bot.py" || true)
if [ -z "$PIDS" ]; then
  echo "Kevin Bot is not running."
else
  echo "Kevin Bot running (PIDs): $PIDS"
  for pid in $PIDS; do
    ps -o pid,cmd,etime -p "$pid" 2>/dev/null || true
  done
fi

# Find latest log file
LAST_LOG=$(ls -1t "$DESKTOP_PATH"/Kevin_Log_*.txt 2>/dev/null | head -n 1 || true)
if [ -n "$LAST_LOG" ]; then
  echo "Latest log: $LAST_LOG"
  if [ "$TAIL" -gt 0 ]; then
    echo "--- Last $TAIL lines of log ---"
    tail -n "$TAIL" "$LAST_LOG" || true
  elif [ "$VERBOSE" -eq 1 ]; then
    echo "--- Last 10 lines of log ---"
    tail -n 10 "$LAST_LOG" || true
  fi
else
  echo "No log file found at $DESKTOP_PATH"
fi

# Show persistent reminders count if file exists
REM_FILE="$DESKTOP_PATH/persistent_reminders.json"
if [ -f "$REM_FILE" ]; then
  COUNT=$(jq -r '. | length' "$REM_FILE" 2>/dev/null || echo "?")
  echo "Persistent reminders stored: $COUNT"
fi

exit 0
