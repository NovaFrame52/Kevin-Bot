import os
import json
import random
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging
import logging.handlers
import re
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime

# Load .env if present
try:
    load_dotenv()
except Exception:
    pass

# Paths and logging (keep Kevin's desktop logging behavior)
ROOT = Path(__file__).parent
DESKTOP_PATH = os.environ.get("KEVIN_DESKTOP_PATH", str(Path.home() / "Desktop"))
DESKTOP_PATH = str(Path(os.path.expanduser(DESKTOP_PATH)))
Path(DESKTOP_PATH).mkdir(parents=True, exist_ok=True)
# use a human-readable timestamp (hyphens between date components and time) in log
LOG_FILE = f"{DESKTOP_PATH}/Kevin_Log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

logger = logging.getLogger("kevin_bot")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

log = logger.info

# Simple config storage (from Ron)
CONFIG_PATH = ROOT / "configs.json"

DEFAULT_PREFIX = os.getenv("PREFIX", "?")  # user's request: new prefix is '?'

if CONFIG_PATH.exists():
    try:
        CONFIGS = json.loads(CONFIG_PATH.read_text())
    except Exception:
        CONFIGS = {}
else:
    CONFIGS = {}


def save_configs():
    try:
        CONFIG_PATH.write_text(json.dumps(CONFIGS, indent=2))
    except Exception as e:
        log(f"Failed to save configs: {e}")


def get_guild_config(guild_id: int):
    # configuration per guild; new fields may be added over time
    return CONFIGS.setdefault(str(guild_id), {
        "prefix": DEFAULT_PREFIX,
        "mod_role": None,
        "log_channel": None,
        "welcome_channel": None,
        # added for enhanced config
        "timezone": None,                  # e.g. "UTC", "America/New_York"
        "reminder_channel": None,          # default channel name for reminders
        "aliases": {},                     # custom command aliases
    })


# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


async def determine_prefix(bot, message):
    if message.guild:
        cfg = get_guild_config(message.guild.id)
        return commands.when_mentioned_or(cfg.get("prefix", DEFAULT_PREFIX))(bot, message)
    return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)


bot = commands.Bot(command_prefix=determine_prefix, intents=intents, description="Kevin - merged with Ron")

# intercept messages to process custom aliases
@bot.event
async def on_message(message):
    # preserve normal behavior for bots and DMs
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

    cfg = get_guild_config(message.guild.id)
    aliases = cfg.get("aliases", {}) or {}
    prefix = cfg.get("prefix", DEFAULT_PREFIX)
    for alias, expansion in aliases.items():
        if message.content.startswith(prefix + alias):
            # rewrite the command portion and leave remainder intact
            suffix = message.content[len(prefix + alias):]
            message.content = prefix + expansion + suffix
            break

    await bot.process_commands(message)
try:
    bot.remove_command('help')
except Exception:
    pass

# Some utilities
QUOTES = [
    "Be kind. Be curious. - Ron",
    "Small steps every day.",
    "Don't forget to take breaks!",
    "Code, test, iterate."
]


# DM functionality has been removed; the ALLOWED_DM_USER_ID setting is no longer used.


async def log_action(guild, description: str):
    cfg = get_guild_config(guild.id)
    ch_name = cfg.get("log_channel")
    if not ch_name:
        return
    channel = discord.utils.get(guild.text_channels, name=ch_name)
    if not channel:
        return
    try:
        await channel.send(description)
    except Exception:
        pass


@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! {latency}ms")


@bot.tree.command(name="ping")
async def slash_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! {latency}ms")


@bot.command()
async def roll(ctx, dice: str = "1d6"):
    try:
        if "d" not in dice:
            raise ValueError
        parts = dice.split("d")
        n = int(parts[0]) if parts[0] != "" else 1
        m = int(parts[1])
        if n < 1 or m < 1 or n > 100:
            raise ValueError
    except Exception:
        await ctx.send("Usage: !roll NdM (e.g. 2d6, d20). Max 100 dice.")
        return
    rolls = [random.randint(1, m) for _ in range(n)]
    total = sum(rolls)
    await ctx.send(f"🎲 Rolled {dice}: {rolls} (total: {total})")


@bot.tree.command(name="roll")
@app_commands.describe(dice="Dice to roll in NdM format, e.g. 2d6")
async def slash_roll(interaction: discord.Interaction, dice: str = "1d6"):
    try:
        if "d" not in dice:
            raise ValueError
        parts = dice.split("d")
        n = int(parts[0]) if parts[0] != "" else 1
        m = int(parts[1])
        if n < 1 or m < 1 or n > 100:
            raise ValueError
    except Exception:
        await interaction.response.send_message("Usage: /roll NdM (e.g. /roll 2d6). Max 100 dice.", ephemeral=True)
        return
    rolls = [random.randint(1, m) for _ in range(n)]
    total = sum(rolls)
    await interaction.response.send_message(f"🎲 Rolled {dice}: {rolls} (total: {total})")


@bot.command()
async def quote(ctx):
    await ctx.send(random.choice(QUOTES))


@bot.tree.command(name="quote")
async def slash_quote(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(QUOTES))


# About command – provide information about Kevin’s capabilities
@bot.command()
async def about(ctx):
    embed = discord.Embed(
        title="🤖 Kevin Bot",
        description=(
            "A simple Discord helper for reminders, moderation, and utilities. "
            "Made with ❤️ to help you stay on top of tasks and keep your server "
            "organized."
        ),
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Features",
        value=(
            "⏰ Schedule one‑off or recurring reminders, "
            "🛠️ perform basic moderation actions, and "
            "⚙️ tweak behaviour with per‑guild settings."
        ),
        inline=False
    )
    embed.add_field(
        name="Commands",
        value=(
            "`?remind` `?myreminders` `?ping` `?roll` `?quote` "
            "`?purge` `?kick` `?ban` `?mute` `?unmute` `?config` "
            "`?about`"
        ),
        inline=False
    )
    embed.add_field(
        name="Configuration",
        value=(
            "`?config show` `?config prefix` `?config timezone` `?config alias_add` "
            "etc. (also available as slash commands)"
        ),
        inline=False
    )
    embed.add_field(
        name="More info",
        value=(
            "Source: https://github.com/Kevin-Bot \n"  # placeholder link
            "Type `?help` or `/help` for details"
        ),
        inline=False
    )
    embed.set_footer(text="Use both prefix (?) and slash (/) commands!")
    await ctx.send(embed=embed)


@bot.tree.command(name="about")
async def slash_about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Kevin Bot",
        description=(
            "A simple Discord helper for reminders, moderation, and utilities. "
            "Made with ❤️ to help you stay on top of tasks and keep your server "
            "organized."
        ),
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Features",
        value=(
            "⏰ Schedule one‑off or recurring reminders, "
            "🛠️ perform basic moderation actions, and "
            "⚙️ tweak behaviour with per‑guild settings."
        ),
        inline=False
    )
    embed.add_field(
        name="Commands",
        value=(
            "`/remind` `/myreminders` `/ping` `/roll` `/quote` "
            "`/purge` `/kick` `/ban` `/mute` `/unmute` `/config` "
            "`/about`"
        ),
        inline=False
    )
    embed.add_field(
        name="Configuration",
        value=(
            "`/config show` `/config prefix` `/config timezone` `/config alias_add` "
            "etc."
        ),
        inline=False
    )
    embed.add_field(
        name="More info",
        value=(
            "Source: https://github.com/Kevin-Bot \n"
            "Type `?help` or `/help` for details"
        ),
        inline=False
    )
    embed.set_footer(text="Use both prefix (?) and slash (/) commands!")
    await interaction.response.send_message(embed=embed)


# Simple remind (Ron style) — not the Kevin persistent system
@bot.command()
async def remind(ctx, minutes: float, *, message: str):
    if minutes <= 0:
        await ctx.send("Please provide a positive number of minutes.")
        return
    await ctx.send(f"Okay {ctx.author.mention}, I'll remind you in {minutes} minute(s).")

    async def _reminder(delay, user, content):
        await asyncio.sleep(delay)
        try:
            await user.send(f"⏰ Reminder: {content}")
        except Exception:
            # fallback to a general channel named 'general' in user's first guild if possible
            channel = None
            try:
                if user.guilds:
                    channel = discord.utils.get(user.guilds[0].text_channels, name="general")
            except Exception:
                pass
            if channel:
                await channel.send(f"{user.mention} ⏰ Reminder: {content}")

    asyncio.create_task(_reminder(minutes * 60, ctx.author, message))


@bot.tree.command(name="remind")
@app_commands.describe(minutes="Minutes until reminder", message="Reminder message")
async def slash_remind(interaction: discord.Interaction, minutes: float, message: str):
    if minutes <= 0:
        await interaction.response.send_message("Please provide a positive number of minutes.", ephemeral=True)
        return
    await interaction.response.send_message(f"Okay {interaction.user.mention}, I'll remind you in {minutes} minute(s).", ephemeral=True)

    async def _reminder(delay, user, content):
        await asyncio.sleep(delay)
        try:
            await user.send(f"⏰ Reminder: {content}")
        except Exception:
            try:
                if user.guilds:
                    channel = discord.utils.get(user.guilds[0].text_channels, name="general")
                else:
                    channel = None
            except Exception:
                channel = None
            if channel:
                await channel.send(f"{user.mention} ⏰ Reminder: {content}")

    asyncio.create_task(_reminder(minutes * 60, interaction.user, message))


# DM commands have been removed per project decision.
# Direct messaging other users via the bot is no longer supported.


# Moderation commands (Ron)
@bot.command()
async def purge(ctx, limit: int = 10):
    cfg = get_guild_config(ctx.guild.id)
    mod_role = cfg.get("mod_role")
    if not (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(ctx.guild.roles, name=mod_role)
            if not (role and role in ctx.author.roles):
                await ctx.send("You don't have permission to do that.")
                return
        else:
            await ctx.send("You don't have permission to do that.")
            return
    deleted = await ctx.channel.purge(limit=limit)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    await log_action(ctx.guild, f"{ctx.author} purged {len(deleted)} messages in #{ctx.channel.name}.")


@bot.tree.command(name="purge")
@app_commands.describe(limit="Number of recent messages to delete")
async def slash_purge(interaction: discord.Interaction, limit: int = 10):
    if not interaction.guild:
        await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    mod_role = cfg.get("mod_role")
    user = interaction.user
    if not (user.guild_permissions.administrator or user.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(interaction.guild.roles, name=mod_role)
            if not (role and role in user.roles):
                await interaction.response.send_message("You don't have permission.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return
    deleted = await interaction.channel.purge(limit=limit)
    await interaction.response.send_message(f"Deleted {len(deleted)} messages.", ephemeral=True)
    await log_action(interaction.guild, f"{interaction.user} purged {len(deleted)} messages in #{interaction.channel.name}.")


@bot.command()
async def kick(ctx, member: discord.Member, *, reason: str = None):
    cfg = get_guild_config(ctx.guild.id)
    mod_role = cfg.get("mod_role")
    if not (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(ctx.guild.roles, name=mod_role)
            if not (role and role in ctx.author.roles):
                await ctx.send("You don't have permission to do that.")
                return
        else:
            await ctx.send("You don't have permission to do that.")
            return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member}.")
        await log_action(ctx.guild, f"{ctx.author} kicked {member}. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"Failed to kick: {e}")


@bot.tree.command(name="kick")
@app_commands.describe(member="Member to kick", reason="Reason for the kick")
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    # reuse permission check logic from earlier
    cfg = get_guild_config(interaction.guild.id)
    mod_role = cfg.get("mod_role")
    user = interaction.user
    if not (user.guild_permissions.administrator or user.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(interaction.guild.roles, name=mod_role)
            if not (role and role in user.roles):
                await interaction.response.send_message("You don't have permission.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member}.")
        await log_action(interaction.guild, f"{interaction.user} kicked {member}. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to kick: {e}", ephemeral=True)


@bot.command()
async def ban(ctx, member: discord.Member, days: int = 0, *, reason: str = None):
    cfg = get_guild_config(ctx.guild.id)
    mod_role = cfg.get("mod_role")
    if not (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(ctx.guild.roles, name=mod_role)
            if not (role and role in ctx.author.roles):
                await ctx.send("You don't have permission to do that.")
                return
        else:
            await ctx.send("You don't have permission to do that.")
            return
    try:
        await member.ban(reason=reason, delete_message_days=days)
        await ctx.send(f"Banned {member}.")
        await log_action(ctx.guild, f"{ctx.author} banned {member}. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"Failed to ban: {e}")


@bot.tree.command(name="ban")
@app_commands.describe(member="Member to ban", days="Delete message history days (0-7)", reason="Reason for ban")
async def slash_ban(interaction: discord.Interaction, member: discord.Member, days: int = 0, reason: str = None):
    cfg = get_guild_config(interaction.guild.id)
    mod_role = cfg.get("mod_role")
    user = interaction.user
    if not (user.guild_permissions.administrator or user.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(interaction.guild.roles, name=mod_role)
            if not (role and role in user.roles):
                await interaction.response.send_message("You don't have permission.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return
    try:
        await member.ban(reason=reason, delete_message_days=days)
        await interaction.response.send_message(f"Banned {member}.")
        await log_action(interaction.guild, f"{interaction.user} banned {member}. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to ban: {e}", ephemeral=True)


@bot.command()
async def mute(ctx, member: discord.Member, minutes: int = 0):
    cfg = get_guild_config(ctx.guild.id)
    mod_role = cfg.get("mod_role")
    if not (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(ctx.guild.roles, name=mod_role)
            if not (role and role in ctx.author.roles):
                await ctx.send("You don't have permission to do that.")
                return
        else:
            await ctx.send("You don't have permission to do that.")
            return
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name="Ron Muted")
    if not role:
        role = await guild.create_role(name="Ron Muted", reason="Created for muting by Ron")
        for ch in guild.text_channels:
            try:
                await ch.set_permissions(role, send_messages=False, add_reactions=False)
            except Exception:
                pass
    try:
        await member.add_roles(role)
        await ctx.send(f"Muted {member}.")
        await log_action(guild, f"{ctx.author} muted {member}.")
        if minutes > 0:
            async def _unmute_after(delay, gm, m, r):
                await asyncio.sleep(delay)
                try:
                    await m.remove_roles(r)
                    await log_action(gm, f"Auto-unmuted {m} after {minutes} minute(s).")
                except Exception:
                    pass
            asyncio.create_task(_unmute_after(minutes * 60, guild, member, role))
    except Exception as e:
        await ctx.send(f"Failed to mute: {e}")


@bot.tree.command(name="mute")
@app_commands.describe(member="Member to mute", minutes="Minutes to auto-unmute (optional)")
async def slash_mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 0):
    cfg = get_guild_config(interaction.guild.id)
    mod_role = cfg.get("mod_role")
    user = interaction.user
    if not (user.guild_permissions.administrator or user.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(interaction.guild.roles, name=mod_role)
            if not (role and role in user.roles):
                await interaction.response.send_message("You don't have permission.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Ron Muted")
    if not role:
        role = await guild.create_role(name="Ron Muted", reason="Created for muting by Ron")
        for ch in guild.text_channels:
            try:
                await ch.set_permissions(role, send_messages=False, add_reactions=False)
            except Exception:
                pass
    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"Muted {member}.")
        await log_action(guild, f"{interaction.user} muted {member}.")
        if minutes > 0:
            async def _unmute_after(delay, gm, m, r):
                await asyncio.sleep(delay)
                try:
                    await m.remove_roles(r)
                    await log_action(gm, f"Auto-unmuted {m} after {minutes} minute(s).")
                except Exception:
                    pass
            asyncio.create_task(_unmute_after(minutes * 60, guild, member, role))
    except Exception as e:
        await interaction.response.send_message(f"Failed to mute: {e}", ephemeral=True)


@bot.command()
async def unmute(ctx, member: discord.Member):
    cfg = get_guild_config(ctx.guild.id)
    mod_role = cfg.get("mod_role")
    if not (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(ctx.guild.roles, name=mod_role)
            if not (role and role in ctx.author.roles):
                await ctx.send("You don't have permission to do that.")
                return
        else:
            await ctx.send("You don't have permission to do that.")
            return
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name="Ron Muted")
    if not role:
        await ctx.send("No mute role exists.")
        return
    try:
        await member.remove_roles(role)
        await ctx.send(f"Unmuted {member}.")
        await log_action(guild, f"{ctx.author} unmuted {member}.")
    except Exception as e:
        await ctx.send(f"Failed to unmute: {e}")


@bot.tree.command(name="unmute")
@app_commands.describe(member="Member to unmute")
async def slash_unmute(interaction: discord.Interaction, member: discord.Member):
    cfg = get_guild_config(interaction.guild.id)
    mod_role = cfg.get("mod_role")
    user = interaction.user
    if not (user.guild_permissions.administrator or user.guild_permissions.manage_guild):
        if mod_role:
            role = discord.utils.get(interaction.guild.roles, name=mod_role)
            if not (role and role in user.roles):
                await interaction.response.send_message("You don't have permission.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Ron Muted")
    if not role:
        await interaction.response.send_message("No mute role exists.", ephemeral=True)
        return
    try:
        await member.remove_roles(role)
        await interaction.response.send_message(f"Unmuted {member}.")
        await log_action(guild, f"{interaction.user} unmuted {member}.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to unmute: {e}", ephemeral=True)


# Modset group (view and set prefix, mod role, log/welcome channels)
@commands.guild_only()
@bot.group(name="modset", invoke_without_command=True)
async def modset(ctx):
    cfg = get_guild_config(ctx.guild.id)
    # build a summary including extended fields
    aliases = cfg.get('aliases') or {}
    alias_list = ', '.join(f"{k}->{v}" for k, v in aliases.items()) if aliases else 'none'
    msg = (
        f"Prefix: {cfg.get('prefix')}\n"
        f"Mod role: {cfg.get('mod_role')}\n"
        f"Log channel: {cfg.get('log_channel')}\n"
        f"Welcome channel: {cfg.get('welcome_channel')}\n"
        f"Timezone: {cfg.get('timezone')}\n"
        f"Reminder channel: {cfg.get('reminder_channel')}\n"
        f"Aliases: {alias_list}"
    )
    await ctx.send(msg)


@modset.command(name="prefix")
@commands.has_permissions(manage_guild=True)
async def modset_prefix(ctx, prefix: str):
    cfg = get_guild_config(ctx.guild.id)
    cfg["prefix"] = prefix
    save_configs()
    await ctx.send(f"Prefix set to {prefix}")


@modset.command(name="modrole")
@commands.has_permissions(manage_guild=True)
async def modset_modrole(ctx, *, role_name: str):
    cfg = get_guild_config(ctx.guild.id)
    cfg["mod_role"] = role_name
    save_configs()
    await ctx.send(f"Mod role set to {role_name}")


@modset.command(name="logchannel")
@commands.has_permissions(manage_guild=True)
async def modset_logchannel(ctx, channel_name: str):
    cfg = get_guild_config(ctx.guild.id)
    cfg["log_channel"] = channel_name
    save_configs()
    await ctx.send(f"Log channel set to {channel_name}")


@modset.command(name="welcome")
@commands.has_permissions(manage_guild=True)
async def modset_welcome(ctx, channel_name: str):
    cfg = get_guild_config(ctx.guild.id)
    cfg["welcome_channel"] = channel_name
    save_configs()
    await ctx.send(f"Welcome channel set to {channel_name}")


# Website monitoring support has been removed to simplify the project and remove external HTTP dependencies.
# (aiohttp is no longer required.)


@bot.event
async def on_ready():
    log(f'Bot is online as {bot.user}')
    try:
        await bot.tree.sync()
        log("Synced application (slash) commands with Discord")
    except Exception as e:
        log(f"Failed to sync application commands: {e}")
    # website monitor disabled (feature removed)


# configuration helpers
@bot.group(name="config")
@commands.has_permissions(manage_guild=True)
async def config(ctx):
    """View or change guild configuration. Available subcommands: show, prefix, modrole,
    logchannel, welcome, timezone, remindchan, alias."""
    if ctx.invoked_subcommand is None:
        await ctx.send("Usage: config <subcommand> (show|prefix|modrole|logchannel|welcome|timezone|remindchan|alias)")


@config.command(name="show")
async def config_show(ctx):
    cfg = get_guild_config(ctx.guild.id)
    # use simple string concatenation to avoid confusing backticks inside an f-string
    await ctx.send("```\n" + json.dumps(cfg, indent=2) + "\n```")


@config.command(name="prefix")
async def config_prefix(ctx, new_prefix: str):
    cfg = get_guild_config(ctx.guild.id)
    cfg["prefix"] = new_prefix
    save_configs()
    await ctx.send(f"Prefix set to `{new_prefix}`")


@config.command(name="modrole")
async def config_modrole(ctx, *, role_name: str = None):
    cfg = get_guild_config(ctx.guild.id)
    cfg["mod_role"] = role_name
    save_configs()
    await ctx.send(f"Mod role set to `{role_name}`")


@config.command(name="logchannel")
async def config_logchannel(ctx, *, channel_name: str = None):
    cfg = get_guild_config(ctx.guild.id)
    cfg["log_channel"] = channel_name
    save_configs()
    await ctx.send(f"Log channel set to `{channel_name}`")


@config.command(name="welcome")
async def config_welcome(ctx, *, channel_name: str = None):
    cfg = get_guild_config(ctx.guild.id)
    cfg["welcome_channel"] = channel_name
    save_configs()
    await ctx.send(f"Welcome channel set to `{channel_name}`")


@config.command(name="timezone")
async def config_timezone(ctx, timezone: str = None):
    cfg = get_guild_config(ctx.guild.id)
    cfg["timezone"] = timezone
    save_configs()
    await ctx.send(f"Timezone set to `{timezone}`")


@config.command(name="remindchan")
async def config_remindchan(ctx, *, channel_name: str = None):
    cfg = get_guild_config(ctx.guild.id)
    cfg["reminder_channel"] = channel_name
    save_configs()
    await ctx.send(f"Default reminder channel set to `{channel_name}`")


@config.group(name="alias")
async def config_alias(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Usage: config alias add|remove|list")


@config_alias.command(name="add")
async def config_alias_add(ctx, alias: str, *, expansion: str):
    cfg = get_guild_config(ctx.guild.id)
    al = cfg.setdefault("aliases", {})
    al[alias] = expansion
    save_configs()
    await ctx.send(f"Alias `{alias}` -> `{expansion}` added.")


@config_alias.command(name="remove")
async def config_alias_remove(ctx, alias: str):
    cfg = get_guild_config(ctx.guild.id)
    al = cfg.get("aliases", {})
    if alias in al:
        del al[alias]
        save_configs()
        await ctx.send(f"Alias `{alias}` removed.")
    else:
        await ctx.send(f"No alias named `{alias}`")


@config_alias.command(name="list")
async def config_alias_list(ctx):
    cfg = get_guild_config(ctx.guild.id)
    al = cfg.get("aliases", {})
    if al:
        lines = "\n".join(f"{k} -> {v}" for k, v in al.items())
        await ctx.send(f"Aliases:\n{lines}")
    else:
        await ctx.send("No aliases defined.")


# Slash command group for configuration
config_group = app_commands.Group(name="config", description="View or change guild configuration")

@config_group.command(name="show")
async def slash_config_show(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    await interaction.response.send_message("```\n" + json.dumps(cfg, indent=2) + "\n```", ephemeral=True)

@config_group.command(name="prefix")
@app_commands.describe(new_prefix="New command prefix")
async def slash_config_prefix(interaction: discord.Interaction, new_prefix: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    cfg["prefix"] = new_prefix
    save_configs()
    await interaction.response.send_message(f"Prefix set to `{new_prefix}`", ephemeral=True)

@config_group.command(name="timezone")
@app_commands.describe(timezone="Time zone identifier, e.g. UTC or America/New_York")
async def slash_config_timezone(interaction: discord.Interaction, timezone: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    cfg["timezone"] = timezone
    save_configs()
    await interaction.response.send_message(f"Timezone set to `{timezone}`", ephemeral=True)

@config_group.command(name="remindchan")
@app_commands.describe(channel_name="Channel name to use for reminders by default")
async def slash_config_remindchan(interaction: discord.Interaction, channel_name: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    cfg["reminder_channel"] = channel_name
    save_configs()
    await interaction.response.send_message(f"Default reminder channel set to `{channel_name}`", ephemeral=True)


# alias subcommands
@config_group.command(name="alias_add")
@app_commands.describe(alias="alias text", expansion="command to run")
async def slash_config_alias_add(interaction: discord.Interaction, alias: str, expansion: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    al = cfg.setdefault("aliases", {})
    al[alias] = expansion
    save_configs()
    await interaction.response.send_message(f"Alias `{alias}` -> `{expansion}` added.", ephemeral=True)

@config_group.command(name="alias_remove")
@app_commands.describe(alias="alias to remove")
async def slash_config_alias_remove(interaction: discord.Interaction, alias: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    al = cfg.get("aliases", {})
    if alias in al:
        del al[alias]
        save_configs()
        await interaction.response.send_message(f"Alias `{alias}` removed.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Alias `{alias}` not found.", ephemeral=True)

@config_group.command(name="alias_list")
async def slash_config_alias_list(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("You must have Manage Server permission.", ephemeral=True)
        return
    cfg = get_guild_config(interaction.guild.id)
    al = cfg.get("aliases", {})
    if al:
        lines = "\n".join(f"{k} -> {v}" for k, v in al.items())
        await interaction.response.send_message(f"Aliases:\n{lines}", ephemeral=True)
    else:
        await interaction.response.send_message("No aliases defined.", ephemeral=True)

# register the group
bot.tree.add_command(config_group)

# Admin command to force-sync application commands
@bot.command()
@commands.has_permissions(administrator=True)
async def synccommands(ctx):
    """Force-sync slash/application commands with Discord (admin only)."""
    try:
        await bot.tree.sync()
        await ctx.send("✅ Synced application (slash) commands with Discord.")
        log(f"{ctx.author} triggered command sync")
    except Exception as e:
        await ctx.send(f"Failed to sync commands: {e}")
        log(f"Manual sync failed: {e}")


@bot.tree.command(name="synccommands")
async def slash_synccommands(interaction: discord.Interaction):
    if not getattr(interaction.user, 'guild_permissions', None) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be a server administrator to use this.", ephemeral=True)
        return
    try:
        await bot.tree.sync()
        await interaction.response.send_message("✅ Synced application (slash) commands with Discord.")
        log(f"{interaction.user} (slash) triggered command sync")
    except Exception as e:
        await interaction.response.send_message(f"Failed to sync commands: {e}", ephemeral=True)
        log(f"Manual slash sync failed: {e}")


# Run
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    logger.error("DISCORD_TOKEN environment variable not set. Set it and restart.")
    raise SystemExit("Missing DISCORD_TOKEN")

if __name__ == '__main__':
    bot.run(TOKEN)
