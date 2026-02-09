# Kevin Bot v1.1.0 Release Notes

**Release Date:** February 8, 2026

## What's New

### 🚀 Installation Improvements
- **Simplified Setup**: Renamed `install_all.sh` to the more intuitive `install.sh`
- **Automatic Man Page**: Man pages are now installed automatically during setup - no need for separate flags
- **Better Script Management**: All installation scripts have been consolidated and merged for better maintainability
- **Executable by Default**: All shell scripts are now properly set as executable

### 📝 Removed Complexity
- Removed the `--install-man` flag (functionality is now automatic)
- Removed the `--install-systemd` flag (use systemd directly if needed)

## How to Update

If you're upgrading from v1.0.1:

```bash
# Pull the latest changes
git pull

# Make scripts executable
chmod +x install.sh && chmod +x Scripts/*.sh

# Reinstall (will use new simplified process)
./install.sh -f
```

## Recommended Usage

```bash
# Start the bot
./Scripts/run.sh

# Check status
./Scripts/kevin-status.sh

# View man page
man kevin
```

## Full Details
See [CHANGELOG.md](CHANGELOG.md) for complete changelog history.

## Requirements
- Python 3.8+
- discord.py >= 2.3.0
- python-dotenv >= 1.0.0
- aiohttp >= 3.8.0
- requests >= 2.25.0
- beautifulsoup4 >= 4.9.0
- schedule >= 1.1.0

## Support
For issues, questions, or suggestions, please open an issue on GitHub.

---

**Contributors**: Thanks to all contributors who helped improve Kevin Bot!
