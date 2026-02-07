#!/usr/bin/env bash
set -euo pipefail

# Uninstaller for Kevin Bot
# Usage: ./uninstall_all.sh [-f|--force] [--remove-venv] [--remove-desktop]
# -f, --force: non-interactive (assume yes)
# --remove-venv: delete the .venv directory
# --remove-desktop: remove Kevin_Bot.desktop from Desktop

FORCE=0
REMOVE_VENV=0
REMOVE_DESKTOP=0

while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    --remove-venv) REMOVE_VENV=1; shift ;;
    --remove-desktop) REMOVE_DESKTOP=1; shift ;;
    -h|--help) echo "Usage: $0 [-f|--force] [--remove-venv] [--remove-desktop]"; exit 0 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

echo "Starting Kevin Bot uninstaller..."

# Remove global symlinks
for name in kevin-stop kevin-start kevin-status kevin-log kevin-man kevin-tldr; do
  LINK="/usr/local/bin/$name"
  if [ -L "$LINK" ] || [ -e "$LINK" ]; then
    if [ -w "$(dirname "$LINK")" ]; then
      rm -f "$LINK"
      echo "Removed $LINK"
    else
      if [ "$FORCE" -eq 1 ]; then
        sudo rm -f "$LINK" || true
        echo "Removed $LINK (sudo used)"
      else
        echo "$LINK requires sudo to remove. Proceed? (y/N)"
        read -r ans
        case "$ans" in
          [Yy]|[Yy][Ee][Ss]) sudo rm -f "$LINK" ; echo "Removed $LINK" ;;
          *) echo "Skipped $LINK" ;;
        esac
      fi
    fi
  else
    echo "$LINK not found; skipping."
  fi
done

# Remove man page and tldr if present
MAN_DIR="/usr/local/share/man/man1/kevin.1"
if [ -f "$MAN_DIR" ]; then
  if [ "$FORCE" -eq 1 ]; then
    sudo rm -f "$MAN_DIR" || true
    echo "Removed man page $MAN_DIR"
  else
    echo "Found man page at $MAN_DIR. Remove? (y/N)"
    read -r ans
    case "$ans" in
      [Yy]|[Yy][Ee][Ss]) sudo rm -f "$MAN_DIR" ; echo "Removed man page" ;;
      *) echo "Skipped man page" ;;
    esac
  fi
fi

TLDR_PAGE="/usr/local/share/tldr/kevin.md"
if [ -f "$TLDR_PAGE" ]; then
  if [ "$FORCE" -eq 1 ]; then
    sudo rm -f "$TLDR_PAGE" || true
    echo "Removed tldr page $TLDR_PAGE"
  else
    echo "Found tldr page at $TLDR_PAGE. Remove? (y/N)"
    read -r ans
    case "$ans" in
      [Yy]|[Yy][Ee][Ss]) sudo rm -f "$TLDR_PAGE" ; echo "Removed tldr page" ;;
      *) echo "Skipped tldr page" ;;
    esac
  fi
fi

# Desktop entry removal (prompt unless --remove-desktop or --force)
HOME_DESKTOP="${KEVIN_DESKTOP_PATH:-$HOME/Desktop}"
if [ -f "$HOME_DESKTOP/Kevin_Bot.desktop" ]; then
  if [ "$REMOVE_DESKTOP" -eq 1 ] || [ "$FORCE" -eq 1 ]; then
    rm -f "$HOME_DESKTOP/Kevin_Bot.desktop"
    echo "Removed $HOME_DESKTOP/Kevin_Bot.desktop"
  else
    echo "Found $HOME_DESKTOP/Kevin_Bot.desktop. Remove? (y/N)"
    read -r ans
    case "$ans" in
      [Yy]|[Yy][Ee][Ss]) rm -f "$HOME_DESKTOP/Kevin_Bot.desktop"; echo "Removed $HOME_DESKTOP/Kevin_Bot.desktop" ;;
      *) echo "Skipped desktop entry" ;;
    esac
  fi
else
  echo "No desktop entry found at $HOME_DESKTOP; skipping."
fi

# Remove .venv if requested
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
  else
    echo ".venv not found; skipping."
  fi
fi

echo "Uninstall complete. Note: kevin.env and your source files were not removed.";
exit 0
