#!/usr/bin/env bash
set -euo pipefail

# Simple stop script for Kevin Bot
# Usage: stop.sh [-f|--force]
# Use -f/--force to avoid interactive prompts

FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    -h|--help) echo "Usage: $0 [-f|--force]"; exit 0 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# Find running Kevin_Bot.py processes
PIDS=$(pgrep -f "Kevin_Bot.py" || true)
if [ -z "$PIDS" ]; then
  echo "No Kevin Bot process found." >&2
  exit 0
fi

echo "Found Kevin Bot PIDs: $PIDS"

if [ "$FORCE" -eq 0 ]; then
  read -r -p "Send SIGTERM to stop them gracefully? (y/N) " answer
  case "$answer" in
    [Yy]|[Yy][Ee][Ss]) ;;
    *) echo "Aborting."; exit 1 ;;
  esac
else
  echo "--force provided; proceeding without prompt."
fi

# Send SIGTERM
for pid in $PIDS; do
  echo "Sending SIGTERM to $pid..."
  kill -TERM "$pid" || true
done

# Wait for processes to exit (up to 10s)
timeout=10
elapsed=0
while [ $elapsed -lt $timeout ]; do
  sleep 1
  elapsed=$((elapsed+1))
  STILL=$(pgrep -f "Kevin_Bot.py" || true)
  if [ -z "$STILL" ]; then
    echo "Processes stopped."; exit 0
  fi
done

# Force kill if still running
STILL=$(pgrep -f "Kevin_Bot.py" || true)
if [ -n "$STILL" ]; then
  echo "Processes still running after $timeout seconds: $STILL"
  if [ "$FORCE" -eq 0 ]; then
    read -r -p "Send SIGKILL to force kill? (y/N) " answer
    case "$answer" in
      [Yy]|[Yy][Ee][Ss]) ;;
      *) echo "Aborting."; exit 1 ;;
    esac
  else
    echo "--force provided; sending SIGKILL."
  fi
  for pid in $STILL; do
    echo "Killing $pid..."
    kill -KILL "$pid" || true
  done
fi

echo "Done."; exit 0
