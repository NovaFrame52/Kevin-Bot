#!/usr/bin/env bash
set -euo pipefail

# Install helper to allow running 'kevin-stop' from anywhere
# Usage: ./install_stop.sh (may prompt for sudo)

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
TARGET="$SCRIPT_DIR/stop.sh"
LINK="/usr/local/bin/kevin-stop"

if [ ! -f "$TARGET" ]; then
  echo "stop.sh not found at: $TARGET" >&2
  exit 1
fi

if [ ! -x "$TARGET" ]; then
  echo "Making $TARGET executable..."
  chmod +x "$TARGET" || true
fi

if [ -w "$(dirname "$LINK")" ]; then
  ln -sf "$TARGET" "$LINK"
  echo "Installed $LINK -> $TARGET"
else
  echo "Creating symlink in /usr/local/bin requires sudo..."
  sudo ln -sf "$TARGET" "$LINK"
  echo "Installed $LINK -> $TARGET (via sudo)"
fi

echo "You can now run 'kevin-stop' from anywhere. Use '-f' to force non-interactive."