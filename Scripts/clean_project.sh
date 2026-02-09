#!/usr/bin/env bash
set -euo pipefail

# Clean project directory: remove logs, caches, compiled files
# Usage: ./clean_project.sh [-f|--force] [--remove-venv] [--remove-desktop] [--ensure]
# --ensure: silently create common project directories if missing

FORCE=0
REMOVE_VENV=0
REMOVE_DESKTOP=0
ENSURE=0
VERBOSE=0

while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    --remove-venv) REMOVE_VENV=1; shift ;;
    --remove-desktop) REMOVE_DESKTOP=1; shift ;;
    --ensure) ENSURE=1; shift ;;
    -v|--verbose) VERBOSE=1; shift ;;
    -h|--help) echo "Usage: $0 [-f|--force] [--remove-venv] [--remove-desktop] [--ensure] [-v|--verbose]"; exit 0 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# Resolve script/project root so operations are consistent
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# If --ensure: silently create common directories and optionally .venv
if [ "$ENSURE" -eq 1 ]; then
  # Load kevin.env if present to get KEVIN_DESKTOP_PATH (project root)
  if [ -f "$PROJECT_ROOT/kevin.env" ]; then
    # shellcheck disable=SC1091
    set -a
    . "$PROJECT_ROOT/kevin.env"
    set +a
  fi

  if [ -n "${KEVIN_DESKTOP_PATH:-}" ]; then
    HOME_DESKTOP="$(eval echo \"$KEVIN_DESKTOP_PATH\")"
  else
    HOME_DESKTOP="$HOME/Desktop"
  fi
  if [ ! -d "$HOME_DESKTOP" ]; then
    mkdir -p "$HOME_DESKTOP" || true
    if [ "$VERBOSE" -eq 1 ]; then
      echo "Created directory: $HOME_DESKTOP"
    fi
  else
    if [ "$VERBOSE" -eq 1 ]; then
      echo "Directory already exists: $HOME_DESKTOP"
    fi
  fi

  if [ ! -d ".venv" ]; then
    if command -v python3 >/dev/null 2>&1; then
      python3 -m venv .venv || true
      if [ "$VERBOSE" -eq 1 ]; then
        echo "Created virtualenv: .venv"
      fi
    fi
  else
    if [ "$VERBOSE" -eq 1 ]; then
      echo ".venv already exists"
    fi
  fi

  # touched a file so version control can note directory intent if needed
  touch .project_dirs_present || true
  if [ "$VERBOSE" -eq 1 ]; then
    echo "Ensure complete."
  fi

  exit 0
fi

echo "Cleaning project directory..."

# Remove python caches and compiled files
find . -type d -name "__pycache__" -exec rm -rf {} + || true
find . -type f -name "*.pyc" -delete || true

# Remove logs and persistent reminders
rm -f Kevin_Log_*.txt persistent_reminders.json || true

# Optionally remove desktop entry
HOME_DESKTOP="${KEVIN_DESKTOP_PATH:-$HOME/Desktop}"
if [ "$REMOVE_DESKTOP" -eq 1 ]; then
  if [ -f "$HOME_DESKTOP/Kevin_Bot.desktop" ]; then
    rm -f "$HOME_DESKTOP/Kevin_Bot.desktop"
    echo "Removed $HOME_DESKTOP/Kevin_Bot.desktop"
  fi
fi

# Optionally remove .venv
if [ "$REMOVE_VENV" -eq 1 ]; then
  if [ -d .venv ]; then
    if [ "$FORCE" -eq 1 ]; then
      rm -rf .venv
      echo "Removed .venv"
    else
      echo "Remove .venv? (y/N)"
      read -r ans
      case "$ans" in
        [Yy]|[Yy][Ee][Ss]) rm -rf .venv; echo "Removed .venv" ;;
        *) echo "Skipped removing .venv" ;;
      esac
    fi
  fi
fi

echo "Clean complete."; exit 0
