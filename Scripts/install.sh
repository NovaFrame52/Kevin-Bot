#!/usr/bin/env bash
set -euo pipefail

# Unified installer for Kevin Bot
# Merges functionality of the previous install_all.sh, install_stop.sh,
# and install_systemd_user.sh into a single script.
# Usage: ./install_all.sh [options]

# Defaults
FORCE=0
SYMLINKS=1
DESKTOP=1
SKIP_VENV=0
INSTALL_TLDR=0
ENABLE_LINGER=0

print_usage() {
  cat <<EOF
Usage: $0 [options]
Options:
  -f, --force           Non-interactive (assume yes)
  --no-symlinks         Don't install global symlinks (/usr/local/bin)
  --no-desktop          Don't copy .desktop launcher to Desktop
  --skip-venv           Skip virtualenv creation and pip install
  --install-tldr        Install tldr page
  --enable-linger       When installing systemd, enable linger via loginctl
  --install-all         Do everything (non-interactive)
  -h, --help            Show this help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    --no-symlinks) SYMLINKS=0; shift ;;
    --no-desktop) DESKTOP=0; shift ;;
    --skip-venv) SKIP_VENV=1; shift ;;
    --install-tldr) INSTALL_TLDR=1; shift ;;
    --enable-linger) ENABLE_LINGER=1; shift ;;
    --install-all) FORCE=1; SYMLINKS=1; DESKTOP=1; INSTALL_TLDR=1; SKIP_VENV=0; ENABLE_LINGER=0; shift ;;
    -h|--help) print_usage; exit 0 ;;
    *) echo "Unknown argument: $1"; print_usage; exit 1 ;;
  esac
done

echo "Starting Kevin Bot installer..."

# Resolve script and project root so installer works from any CWD or when invoked via symlink
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || true

# Basic checks
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found. Please install Python 3.8+" >&2
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Using Python $PYTHON_VERSION"

# Create virtualenv and install requirements (in project root)
if [ "$SKIP_VENV" -eq 0 ]; then
  if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtualenv at $PROJECT_ROOT/.venv..."
    python3 -m venv "$PROJECT_ROOT/.venv"
  else
    echo "Virtualenv .venv already exists."
  fi

  # shellcheck disable=SC1091
  . "$PROJECT_ROOT/.venv/bin/activate"

  if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
  else
    echo "requirements.txt not found, skipping pip install.";
  fi
else
  echo "Skipping virtualenv and dependency installation (per --skip-venv)."
fi

# Make helper scripts executable (Scripts/ directory)
for f in "$SCRIPT_DIR"/run.sh "$SCRIPT_DIR"/stop.sh "$SCRIPT_DIR"/clean_project.sh "$SCRIPT_DIR"/kevin-status.sh "$SCRIPT_DIR"/kevin-log.sh "$SCRIPT_DIR"/kevin-man.sh; do
  if [ -f "$f" ]; then
    chmod +x "$f" || true
    echo "Ensured $(basename "$f") is executable"
  fi
done

# Ensure project helper files exist (README, env example)
if [ ! -f "$PROJECT_ROOT/README.md" ]; then
  cat > "$PROJECT_ROOT/README.md" <<'EOF'
# Kevin Bot

Simple Discord bot for reminders.

Quick start:
1. Create `kevin.env` based on `kevin.env.example` and set `DISCORD_TOKEN`.
2. Run `./install_all.sh` to set up the environment and helpers.
3. Start with `./Scripts/run.sh` or `kevin-start` if you installed the symlink.
4. Stop with `kevin-stop`.

Security:
- Keep your `DISCORD_TOKEN` private. `kevin.env` is automatically restricted to `600` permissions during install.

Files created by installer: `.venv`, symlinks `kevin-start`/`kevin-stop`, `Kevin_Bot.desktop` on your Desktop (optional).
EOF
  echo "Created README.md"
fi

if [ ! -f "$PROJECT_ROOT/kevin.env.example" ]; then
  cat > "$PROJECT_ROOT/kevin.env.example" <<'EOF'
# Example environment for Kevin Bot
DISCORD_TOKEN=your_token_here
KEVIN_DESKTOP_PATH=/home/YOURUSER/Desktop/Kevin
EOF
  echo "Created kevin.env.example"
fi

# If kevin.env missing, offer to create it from example (project root)
if [ ! -f "$PROJECT_ROOT/kevin.env" ]; then
  if [ "$FORCE" -eq 1 ]; then
    cp "$PROJECT_ROOT/kevin.env.example" "$PROJECT_ROOT/kevin.env" || true
    chmod 600 "$PROJECT_ROOT/kevin.env" || true
    echo "Created kevin.env from kevin.env.example (forced). Please edit and add your real DISCORD_TOKEN.";
  else
    echo "kevin.env not found. Create kevin.env from example? (y/N)"
    read -r ans
    case "$ans" in
      [Yy]|[Yy][Ee][Ss]) cp "$PROJECT_ROOT/kevin.env.example" "$PROJECT_ROOT/kevin.env" || true; chmod 600 "$PROJECT_ROOT/kevin.env" || true; echo "Created kevin.env; please edit and add your real DISCORD_TOKEN." ;;
      *) echo "kevin.env not created; remember to create it and add DISCORD_TOKEN." ;;
    esac
  fi
fi

# Secure kevin.env if present
if [ -f kevin.env ]; then
  current_perm="$(stat -c %a kevin.env 2>/dev/null || echo "")"
  if [ "$current_perm" != "600" ]; then
    if [ "$FORCE" -eq 1 ]; then
      chmod 600 kevin.env || true
      echo "Set kevin.env permissions to 600 (forced)."
    else
      echo "kevin.env exists and has permissions $current_perm. Change to 600? (y/N)"
      read -r ans
      case "$ans" in
        [Yy]|[Yy][Ee][Ss]) chmod 600 kevin.env || true; echo "Permissions set to 600." ;;
        *) echo "Skipping permission change." ;;
      esac
    fi
  else
    echo "kevin.env permissions already 600."
  fi
else
  echo "kevin.env not found. Create it with your DISCORD_TOKEN if you haven't already.";
fi

# Load kevin.env (silently) to get KEVIN_DESKTOP_PATH for directory checks (project root)
if [ -f "$PROJECT_ROOT/kevin.env" ]; then
  # shellcheck disable=SC1091
  set -a
  . "$PROJECT_ROOT/kevin.env"
  set +a
fi

# Ensure the desktop/log path exists (silent)
if [ -n "${KEVIN_DESKTOP_PATH:-}" ]; then
  HOME_DESKTOP="$(eval echo \"$KEVIN_DESKTOP_PATH\")"
else
  HOME_DESKTOP="$HOME/Desktop"
fi
if [ ! -d "$HOME_DESKTOP" ]; then
  mkdir -p "$HOME_DESKTOP" || true
fi


# Helper: install a symlink, using sudo if necessary (interactive unless forced)
install_symlink() {
  local target=$1 name=$2 link="/usr/local/bin/$2"

  if [ ! -f "$target" ]; then
    echo "Warning: $target not found; skipping $name symlink.";
    return
  fi

  if [ -w "$(dirname "$link")" ]; then
    ln -sf "$target" "$link"
    echo "Installed $link -> $target"
  else
    if [ "$FORCE" -eq 1 ]; then
      sudo ln -sf "$target" "$link"
      echo "Installed $link -> $target (sudo used)."
    else
      echo "Need sudo to install $link. Proceed and use sudo? (y/N)"
      read -r ans
      case "$ans" in
        [Yy]|[Yy][Ee][Ss]) sudo ln -sf "$target" "$link"; echo "Installed $link -> $target" ;;
        *) echo "Skipped $link" ;;
      esac
    fi
  fi
}

# Install symlinks
if [ "$SYMLINKS" -eq 1 ]; then
  install_symlink "$SCRIPT_DIR/stop.sh" kevin-stop
  install_symlink "$SCRIPT_DIR/run.sh" kevin-start
  install_symlink "$SCRIPT_DIR/kevin-status.sh" kevin-status
  install_symlink "$SCRIPT_DIR/kevin-log.sh" kevin-log
  if [ -f "$PROJECT_ROOT/kevin.1" ]; then
    install_symlink "$PROJECT_ROOT/kevin.1" kevin-man
  fi
  if [ -f "$PROJECT_ROOT/tldr-kevin.md" ]; then
    install_symlink "$PROJECT_ROOT/tldr-kevin.md" kevin-tldr
  fi
fi

# Desktop entry
if [ "$DESKTOP" -eq 1 ] && [ -f Kevin_Bot.desktop ]; then
  HOME_DESKTOP="${KEVIN_DESKTOP_PATH:-$HOME/Desktop}"
  mkdir -p "$HOME_DESKTOP"
  cp -f Kevin_Bot.desktop "$HOME_DESKTOP/"
  chmod +x "$HOME_DESKTOP/Kevin_Bot.desktop" || true
  echo "Copied Kevin_Bot.desktop to $HOME_DESKTOP"
fi

# Install man page
if [ -f kevin.1 ]; then
  MAN_DIR="/usr/local/share/man/man1"
  if [ -w "$(dirname "$MAN_DIR")" ]; then
    ln -sf "$(pwd)/kevin.1" "$MAN_DIR/kevin.1" || true
    echo "Installed man page to $MAN_DIR/kevin.1"
  else
    if [ "$FORCE" -eq 1 ]; then
      sudo ln -sf "$(pwd)/kevin.1" "$MAN_DIR/kevin.1" || true
      echo "Installed man page to $MAN_DIR/kevin.1 (sudo used)"
    else
      echo "Need sudo to install man page to $MAN_DIR. Proceed and use sudo? (y/N)"
      read -r ans
      case "$ans" in
        [Yy]|[Yy][Ee][Ss]) sudo ln -sf "$(pwd)/kevin.1" "$MAN_DIR/kevin.1"; echo "Installed man page" ;;
        *) echo "Skipped man page install" ;;
      esac
    fi
  fi
else
  echo "kevin.1 man file not found; skipping man install."
fi

# Install tldr page
if [ "$INSTALL_TLDR" -eq 1 ]; then
  if [ -f tldr-kevin.md ]; then
    TLDR_DIR="/usr/local/share/tldr"
    if [ -w "$(dirname "$TLDR_DIR")" ]; then
      mkdir -p "$TLDR_DIR" || true
      cp -f tldr-kevin.md "$TLDR_DIR/kevin.md"
      echo "Installed tldr page to $TLDR_DIR/kevin.md"
    else
      if [ "$FORCE" -eq 1 ]; then
        sudo mkdir -p "$TLDR_DIR" || true
        sudo cp -f tldr-kevin.md "$TLDR_DIR/kevin.md"
        echo "Installed tldr page to $TLDR_DIR/kevin.md (sudo used)"
      else
        echo "Need sudo to install tldr page to $TLDR_DIR. Proceed and use sudo? (y/N)"
        read -r ans
        case "$ans" in
          [Yy]|[Yy][Ee][Ss]) sudo mkdir -p "$TLDR_DIR"; sudo cp -f tldr-kevin.md "$TLDR_DIR/kevin.md"; echo "Installed tldr page" ;;
          *) echo "Skipped tldr page install" ;;
        esac
      fi
    fi
  else
    echo "tldr-kevin.md not found; skipping tldr install."
  fi
fi

# Function: install systemd --user unit
install_systemd_user() {
  UNIT_DIR="$HOME/.config/systemd/user"
  UNIT_FILE="$UNIT_DIR/kevin.service"

  if ! command -v systemctl >/dev/null 2>&1; then
    echo "systemctl not found; cannot install systemd --user service." >&2
    return 1
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

  echo "Installed systemd user unit to $UNIT_FILE"

  systemctl --user daemon-reload
  systemctl --user enable --now kevin.service || true

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
}

echo "Installing systemd --user unit for kevin..."
install_systemd_user || echo "Failed to install systemd --user unit; you can run this script with --install-systemd manually."

# Summary
echo "\nInstallation complete. Quick actions:"
if [ -f kevin.env ]; then
  echo "- Ensure kevin.env contains your DISCORD_TOKEN and has permissions 600."
else
  echo "- Create kevin.env with your DISCORD_TOKEN: DISCORD_TOKEN=your_token_here";
fi
echo "- Run the bot with: ./Scripts/run.sh or kevin-start (if symlink installed)"
echo "- Stop with: kevin-stop"

echo "Done."
exit 0
