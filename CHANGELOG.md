# Changelog

All notable changes to Kevin Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Current-Release]

## [1.1.0] - 2026-02-08

### Added
- Automatic man page installation (now included by default in the install process)
- All shell scripts are now executable by default

### Changed
- **Simplified Installation**: Renamed `install_all.sh` to `install.sh` for clarity
- **Installation Script Improvements**: Consolidated and merged install scripts for better maintainability
- **Default Behavior**: Man page installation is now automatic instead of requiring a separate flag
- **Update Script**: Enhanced `update.sh` with merged install improvements

### Removed
- `--install-man` flag (man page now installs automatically)
- `--install-systemd` flag (functionality removed, use systemd directly if needed)
- Separate `install_all.sh` script (consolidated into `install.sh`)

### Fixed
- File permission issues - all scripts are now properly executable

### Installation Instructions (v1.1.0)
```bash
# Make scripts executable (one-time)
chmod +x install.sh && chmod +x Scripts/*.sh

# Create your config file
cp kevin.env.example kevin.env
# Edit kevin.env and add your DISCORD_TOKEN

# Install and run (non-interactive)
./install.sh -f
```

### Recommended Usage
```bash
# Start the bot
./Scripts/run.sh

# View status and logs
./Scripts/kevin-status.sh

# Stop the bot
./Scripts/stop.sh

# View man page
man kevin
```

---

## [1.0.1] - Prior Release

### Added
- Privacy Policy documentation
- Terms of Service documentation

### Changed
- Documentation and project governance improvements

---

## [1.0.0] - Initial Release

### Features
- Discord bot for reminders and periodic messages
- Configurable via `.env` file
- Helper scripts for installation, running, stopping, and monitoring
- Man page and TLDR documentation
- Systemd integration support
- Global command shortcuts (when symlinks installed)

### Includes
- `run.sh` - Start the bot with options for force mode and verbose output
- `stop.sh` - Gracefully stop the bot or force kill
- `kevin-status.sh` - Check bot status and view recent logs
- `kevin-log.sh` - Live log viewer with auto-follow
- `install_all.sh` - Complete installation setup
- `update.sh` - Update bot and dependencies

---

## Dependencies
- Python 3.8+
- discord.py >= 2.3.0
- python-dotenv >= 1.0.0
- aiohttp >= 3.8.0
- requests >= 2.25.0
- beautifulsoup4 >= 4.9.0
- schedule >= 1.1.0

## Quick Links
- [README](README.md) - Quick start and usage guide
- [Man Page](kevin.1) - Detailed command reference
- [Privacy Policy](Privacy-Policy.md)
- [Terms of Service](TOS.md)
