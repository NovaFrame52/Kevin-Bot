## Kevin Bot

Kevin is a small Discord bot for reminders and periodic messages.

## Quick start
1. Create `kevin.env` from `kevin.env.example` and add your `DISCORD_TOKEN`.
2. Run `./install_all.sh` (from the project root) to set up the environment and install helpers (pass `-f` for non-interactive).
3. Start the bot with `./Scripts/run.sh` (or the global helper `kevin-start` if you installed symlinks).
4. Stop the bot with `kevin-stop` or `./Scripts/stop.sh`.

## Running (detailed)
- Make scripts executable (one-time):
  - `chmod +x install_all.sh` and `chmod +x Scripts/*.sh` to make all helpers executable.

- Install everything (non-interactive):
  - `./install_all.sh -f`

- Start the bot (examples):
  - `./Scripts/run.sh` (interactive checks)
  - `./Scripts/run.sh -f` (force; bypass prompts)
  - `./Scripts/run.sh -v` (verbose; show created directories)
  - `./Scripts/run.sh -f -v` (force + verbose)
  - If you installed symlinks: `kevin-start` (same as `kevin-start`)

- Stop the bot:
  - `./Scripts/stop.sh` or `kevin-stop`
  - Use `--force` to kill non-interactively: `./Scripts/stop.sh -f`

- Status & logs:
  - `./kevin-status.sh` (shows whether the bot is running and the latest log)
  - `./kevin-status.sh -t 50` (show last 50 log lines)
  - `kevin-status` (if symlink installed)

- Live log viewer:
  - `./kevin-log.sh` (waits for the bot to start if needed, tails the active log until the bot stops)
  - `./kevin-log.sh -t 200` (start showing last 200 lines and follow until the bot exits)
  - `./kevin-log.sh -v` (verbose; shows waiting/created messages)
  - `kevin-log` (if symlink installed)

## Manual page and TLDR
- To install the local man page: `./install_all.sh --install-man` (may prompt for sudo) and then run `man kevin` or `man ./kevin.1` to view locally.
- To install the tldr page: `./install_all.sh --install-tldr` (may prompt for sudo). If you use a local tldr client, you can copy `tldr-kevin.md` into its pages directory; otherwise view the file directly: `less tldr-kevin.md`.

## Suggested output examples

- `kevin-status` (bot running):

```
Kevin Bot running (PIDs): 12345
  PID    CMD                          ELAPSED
 12345   python3 Kevin_Bot.py          01:23:45
Latest log: /home/aster/Desktop/Kevin_Log_20260204_120000.txt
Persistent reminders stored: 2
```

- `kevin-status` (bot not running):

```
Kevin Bot is not running.
No log file found at /home/aster/Desktop
```

- `kevin-log.sh` (when bot starts and runs):

```
[2026-02-04 12:00:00] INFO - Bot is online as KevinBot#1234
[2026-02-04 12:00:05] INFO - Using DESKTOP_PATH: /home/aster/Desktop
[2026-02-04 12:05:00] INFO - Sent random message to #general: Remember to drink water!
... (continues until bot stops) ...
```

- Pre-create common directories or ensure environment (useful before running):
  - `./clean_project.sh --ensure` (creates `.venv` and Desktop path silently)
  - `./clean_project.sh --ensure --verbose` (same, but prints created resources)

- Uninstall helpers:
  - `./uninstall_all.sh` - will prompt
  - `./uninstall_all.sh -f --remove-venv --remove-desktop` - non-interactive remove

## Security
- Keep `kevin.env` private. The installer sets permissions to `600` when creating it.
- If the token is ever exposed, rotate it from the Discord Developer Portal.

## Project layout
- `Kevin_Bot.py` - main bot
- `Scripts/run.sh` - start/run helper
- `Scripts/stop.sh` - stop helper
- `install_all.sh` / `uninstall_all.sh` - full installer/uninstaller
- `requirements.txt` - Python deps

## Support

For issues, check the logs and verify:
1. DISCORD_TOKEN is valid
2. Bot has required intents enabled
3. Network connection is stable

For Suggestions, open an issue or submit a pull request.

---

**Made with ❤️ for wellness and productivity**

Stay hydrated, stay healthy! 💚

