#!/usr/bin/env bash
set -euo pipefail

# One-click runner for Kevin Bot
# Usage: ./run.sh [-f|--force]
# Creates a virtualenv (./.venv), installs requirements, loads kevin.env, and runs the bot.

# Parse args
FORCE=0
VERBOSE=0
while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    -v|--verbose) VERBOSE=1; shift ;;
    -h|--help) echo "Usage: $0 [-f|--force] [-v|--verbose]"; exit 0 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# Resolve script/project root so the script works regardless of CWD or when invoked via symlink
# Use readlink -f to resolve the real path of the script
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Ensure python3 is available
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found; please install Python 3." >&2
  exit 1
fi

# Create venv if missing (in project root)
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
  echo "Creating virtualenv..."
  python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Activate venv
# shellcheck disable=SC1091
. "$PROJECT_ROOT/.venv/bin/activate"

# Upgrade pip and install deps
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"

# Load env vars from kevin.env (if present) in project root and secure it
if [ -f "$PROJECT_ROOT/kevin.env" ]; then
  echo "Found kevin.env — checking permissions and loading environment..."

  # Only set restrictive permissions if they're not already 600
  current_perm="$(stat -c %a "$PROJECT_ROOT/kevin.env" 2>/dev/null || echo "")"
  if [ "$current_perm" != "600" ]; then
    echo "Setting restrictive permissions on kevin.env..."
    chmod 600 "$PROJECT_ROOT/kevin.env" || true
  fi

  # Temporarily load env variables (don't print secrets)
  set -a
  # shellcheck disable=SC1091
  . "$PROJECT_ROOT/kevin.env"
  set +a

  # Ensure desktop/log path exists silently
  if [ -n "${KEVIN_DESKTOP_PATH:-}" ]; then
    DESKTOP_PATH="$(eval echo \"$KEVIN_DESKTOP_PATH\")"
  else
    DESKTOP_PATH="$HOME/Desktop"
  fi
  if [ ! -d "$DESKTOP_PATH" ]; then
    mkdir -p "$DESKTOP_PATH" || true
    if [ "$VERBOSE" -eq 1 ]; then
      echo "Created desktop/log directory: $DESKTOP_PATH"
    fi
  else
    if [ "$VERBOSE" -eq 1 ]; then
      echo "Desktop/log directory exists: $DESKTOP_PATH"
    fi
  fi

  # Basic validation for DISCORD_TOKEN
  if [ -z "${DISCORD_TOKEN:-}" ]; then
    echo "Error: DISCORD_TOKEN not set in kevin.env. Add your token or export DISCORD_TOKEN before running." >&2
    exit 1
  fi

  # Catch common placeholder value
  if [ "${DISCORD_TOKEN}" = "your_token_here" ]; then
    echo "Error: DISCORD_TOKEN in kevin.env looks like the placeholder value. Please replace it with your real token." >&2
    exit 1
  fi

  # Basic malformed-token check (tokens usually contain two dots)
  if [[ "${DISCORD_TOKEN}" != *.*.* ]]; then
    if [ "$FORCE" -eq 1 ]; then
      echo "Warning: DISCORD_TOKEN looks malformed, but --force provided; continuing."
    else
      echo "Warning: DISCORD_TOKEN looks malformed. Continue anyway? (y/N)"
      read -r answer
      case "$answer" in
        [Yy]|[Yy][Ee][Ss]) ;;
        *) echo "Aborting."; exit 1 ;;
      esac
    fi
  fi
fi

echo "Starting Kevin Bot..."
exec python3 "$PROJECT_ROOT/Scripts/Kevin_Bot.py"
