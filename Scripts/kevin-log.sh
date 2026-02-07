#!/usr/bin/env bash
set -euo pipefail

# Tail the active Kevin Bot log from start (or wait for start) until the bot stops
# Usage: kevin-log.sh [-t N|--tail N] [-v|--verbose]
# -t N : show last N lines initially (default 10)
# -v   : verbose mode (show waiting/created messages)

TAIL=10
VERBOSE=0
while [ $# -gt 0 ]; do
  case "$1" in
    -t|--tail) TAIL=${2:-10}; shift 2 || true ;;
    -v|--verbose) VERBOSE=1; shift ;;
    -h|--help) echo "Usage: $0 [-t N|--tail N] [-v|--verbose]"; exit 0 ;;
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

# Helper to get latest log
get_latest_log() {
  ls -1t "$DESKTOP_PATH"/Kevin_Log_*.txt 2>/dev/null | head -n 1 || true
}

# Wait for process to appear (if not running)
wait_for_bot() {
  if pgrep -f "Kevin_Bot.py" >/dev/null 2>&1; then
    return 0
  fi
  if [ "$VERBOSE" -eq 1 ]; then
    echo "Waiting for Kevin Bot to start..."
  fi
  while ! pgrep -f "Kevin_Bot.py" >/dev/null 2>&1; do
    sleep 1
  done
  if [ "$VERBOSE" -eq 1 ]; then
    echo "Kevin Bot started."
  fi
}

# Wait for a log file to appear (timeout 60s)
wait_for_log() {
  local attempts=0
  local logf
  while [ $attempts -lt 60 ]; do
    logf=$(get_latest_log)
    if [ -n "$logf" ]; then
      echo "$logf"
      return 0
    fi
    sleep 1
    attempts=$((attempts+1))
  done
  return 1
}

# Main flow
# 1) Wait for bot to start (if not running)
wait_for_bot

# 2) Find or wait for the most recent log file
LOGFILE=$(get_latest_log)
if [ -z "$LOGFILE" ]; then
  if [ "$VERBOSE" -eq 1 ]; then
    echo "No log file yet; waiting up to 60s for log to be created..."
  fi
  if ! LOGFILE=$(wait_for_log); then
    echo "No log file found in $DESKTOP_PATH; exiting." >&2
    exit 1
  fi
fi

if [ "$VERBOSE" -eq 1 ]; then
  echo "Tailing log file: $LOGFILE"
fi

# Start tail -F in background
tail -n "$TAIL" -F "$LOGFILE" &
TAIL_PID=$!

# When the bot process exits, we stop tailing
while pgrep -f "Kevin_Bot.py" >/dev/null 2>&1; do
  sleep 1
done

# Give a tiny grace period for last writes
sleep 0.5

# Stop tail
if kill -0 "$TAIL_PID" >/dev/null 2>&1; then
  kill "$TAIL_PID" 2>/dev/null || true
  wait "$TAIL_PID" 2>/dev/null || true
fi

if [ "$VERBOSE" -eq 1 ]; then
  echo "Kevin Bot has stopped; exiting log view."
fi

exit 0
