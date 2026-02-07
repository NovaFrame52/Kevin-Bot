#!/usr/bin/env bash
set -euo pipefail

# Install a systemd --user service for Kevin Bot
# Usage: ./install_systemd_user.sh [--enable-linger] [-f|--force]

FORCE=0
ENABLE_LINGER=0
while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    --enable-linger) ENABLE_LINGER=1; shift ;;
    -h|--help) echo "Usage: $0 [--enable-linger] [-f|--force]"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
UNIT_FILE="$UNIT_DIR/kevin.service"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not found; cannot install systemd --user service." >&2
  exit 1
fi

mkdir -p "$UNIT_DIR"

cat > "$UNIT_FILE" <<EOF
[Unit]
Description=Kevin Bot (user)
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_ROOT
ExecStart=$SCRIPT_DIR/run.sh -f
# Load environment from project kevin.env if present
EnvironmentFile=$PROJECT_ROOT/kevin.env
Restart=on-failure
RestartSec=5
# Let systemd capture stdout/stderr (also written to Kevin's log file)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

echo "Installed systemd user unit to $UNIT_FILE"

# Reload and enable
systemctl --user daemon-reload
systemctl --user enable --now kevin.service

if [ $? -eq 0 ]; then
  echo "kevin.service enabled and started (systemd --user)."
else
  echo "Failed to enable/start kevin.service; check 'systemctl --user status kevin.service' for details." >&2
fi

if [ "$ENABLE_LINGER" -eq 1 ]; then
  if command -v loginctl >/dev/null 2>&1; then
    if [ "$FORCE" -eq 1 ]; then
      sudo loginctl enable-linger "$USER" || true
      echo "Enabled linger for $USER (sudo used)."
    else
      echo "Enable linger for $USER to allow services to run without active login? (y/N)"
      read -r ans
      case "$ans" in
        [Yy]|[Yy][Ee][Ss]) sudo loginctl enable-linger "$USER"; echo "Enabled linger for $USER" ;;
        *) echo "Skipped enabling linger" ;;
      esac
    fi
  else
    echo "loginctl not found; cannot enable linger" >&2
  fi
fi

exit 0
