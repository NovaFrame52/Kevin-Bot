kevin
====

> Helper commands for the Kevin Discord bot (start/stop/status/log).

- Start the bot:

`kevin-start`

- Stop the bot gracefully:

`kevin-stop`

- Force-stop the bot:

`kevin-stop --force`

- Show status and last lines of latest log:

`kevin-status -t 20`

- Follow the live log until the bot stops:

`kevin-log -t 200`

- Discord commands (also available as `/` commands in Discord). Prefix is now `?`.

`?remind 5m Hurry up` or `/remind time:5m message:Hurry up persistent:false`

`?myreminders` or `/myreminders`

Admin-only (use `?` prefix or `/` in Discord):

`?setrandominterval 120` — set interval to 2 minutes

`?setrandomcount 2` — send up to 2 random messages per interval

`?randomauto off` — disable automatic randomization

Additional commands merged from Ron:

`?ping` — Pong + latency

`?roll 2d6` — Roll dice

`?quote` — Random short quote

`?dm <member> <message>` — Send DM to member (restricted by config)

Moderation (requires mod role or admin): `?purge`, `?kick`, `?ban`, `?mute`, `?unmute`, and the `?modset` group for settings.

`?synccommands` — (admin) Force Discord slash command sync if needed.
