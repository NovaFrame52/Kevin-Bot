#!/usr/bin/env bash
set -euo pipefail

# Update project from git remote and re-run installer
# Usage: update.sh [-f|--force] [-b|--branch BRANCH] [--url GIT_URL] [--no-restart]

FORCE=0
BRANCH=""
# Default static repo URL (can be overridden with --url)
GIT_URL="https://github.com/NovaFrame52/Kevin-Bot.git"
NO_RESTART=0

while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    -b|--branch) BRANCH="$2"; shift 2 || true ;;
    --url) GIT_URL="$2"; shift 2 || true ;;
    --no-restart) NO_RESTART=1; shift ;;
    -h|--help) echo "Usage: $0 [-f|--force] [-b|--branch BRANCH] [--url GIT_URL] [--no-restart]"; echo "Default repo URL: $GIT_URL"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || true

if ! command -v git >/dev/null 2>&1; then
  echo "git not found; please install git to use update.sh" >&2
  exit 1
fi

if [ ! -d ".git" ]; then
  if [ -n "$GIT_URL" ]; then
    if [ "$FORCE" -eq 0 ]; then
      echo "Repository is not a git repo. Initialize and set origin to $GIT_URL? (y/N)"
      read -r ans
      case "$ans" in
        [Yy]|[Yy][Ee][Ss]) ;;
        *) echo "Aborting."; exit 1 ;;
      esac
    fi
    git init
    git remote add origin "$GIT_URL"
    if [ -n "$BRANCH" ]; then
      git fetch origin "$BRANCH"
      git checkout -t origin/"$BRANCH" || true
    else
      git fetch origin
    fi
  else
    echo "Not a git repository and no --url provided. Run 'git init' or pass --url to clone into this directory." >&2
    exit 1
  fi
fi

# Ensure working tree is clean or force
if [ "$FORCE" -eq 0 ]; then
  if [ -n "$(git status --porcelain)" ]; then
    echo "Repository has local changes. Commit or stash them, or run with -f to force update." >&2
    exit 1
  fi
fi

# Determine branch to pull
if [ -z "$BRANCH" ]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
  BRANCH=${BRANCH:-main}
fi

echo "Updating from origin/$BRANCH..."
# Fetch and pull
git fetch --all --prune
if git rev-parse --verify origin/"$BRANCH" >/dev/null 2>&1; then
  git pull --ff-only origin "$BRANCH" || { echo "Fast-forward failed; try 'git pull' manually or use -f to override."; exit 1; }
else
  echo "Remote branch origin/$BRANCH not found; skipping pull.";
fi

# Re-run installer to ensure deps and symlinks are up-to-date
echo "Re-running installer to refresh deps and symlinks..."
# Use the project's installer with force to auto-setup symlinks
"$SCRIPT_DIR/install_all.sh" -f

# Restart bot if desired
if [ "$NO_RESTART" -eq 0 ]; then
  echo "Restarting Kevin Bot (if running)..."
  "$SCRIPT_DIR/stop.sh" -f || true
  # Start in background with nohup so it survives terminal closing
  nohup "$SCRIPT_DIR/run.sh" -f > /dev/null 2>&1 &
  echo "Kevin Bot started (background)."
fi

exit 0
