import os
import json
import random
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging
import logging.handlers
import re
import aiohttp
import discord
from discord.ext import commands, tasks
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
LOG_FILE = f"{DESKTOP_PATH}/Kevin_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

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
    return CONFIGS.setdefault(str(guild_id), {
        "prefix": DEFAULT_PREFIX,
        "mod_role": None,
        "log_channel": None,
        "welcome_channel": None,
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


ALLOWED_DM_USER_ID = int(os.getenv("ALLOWED_DM_USER_ID", "0")) if os.getenv("ALLOWED_DM_USER_ID") else None


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


# Basic commands (from Ron)
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


# DM command restricted (Ron)
@bot.command(name="dm")
async def dm(ctx, member: discord.Member, *, message: str):
    if ALLOWED_DM_USER_ID and getattr(ctx.author, 'id', None) != ALLOWED_DM_USER_ID:
        await ctx.send("You are not allowed to use this command.")
        return
    try:
        await ctx.message.delete()
    except Exception:
        pass

    attachment = None
    try:
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
    except Exception:
        attachment = None

    try:
        if attachment:
            file = await attachment.to_file()
            await member.send(content=message or None, file=file)
        else:
            m = re.search(r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))", message or "", re.IGNORECASE)
            if m:
                url = m.group(1)
                embed = discord.Embed()
                embed.set_image(url=url)
                await member.send(content=(message or None), embed=embed)
            else:
                await member.send(message or None)
        try:
            await ctx.author.send(f"Sent DM to {member.display_name}.")
        except Exception:
            pass
    except Exception as e:
        try:
            await ctx.author.send(f"Failed to send DM to {member.display_name}: {e}")
        except Exception:
            await ctx.send(f"Failed to send DM: {e}")


@bot.tree.command(name="dm")
@app_commands.describe(target="Member identifier (ID, mention, username#discrim, or name)", message="Message content")
async def slash_dm(interaction: discord.Interaction, target: str, message: str, image: discord.Attachment = None):
    if ALLOWED_DM_USER_ID and getattr(interaction.user, 'id', None) != ALLOWED_DM_USER_ID:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
        return
    if not message:
        await interaction.response.send_message("Missing message content.", ephemeral=True)
        return
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
        return
    resolved = None
    tid = None
    if target.startswith("<@") and target.endswith(">"):
        digits = ''.join(c for c in target if c.isdigit())
        if digits:
            tid = digits
    elif target.isdigit():
        tid = target
    if tid:
        try:
            resolved = guild.get_member(int(tid))
        except Exception:
            resolved = None
    if resolved is None and "#" in target:
        name, discrim = target.rsplit("#", 1)
        for m in guild.members:
            if m.name == name and m.discriminator == discrim:
                resolved = m
                break
    if resolved is None:
        for m in guild.members:
            if m.display_name == target or m.name == target:
                resolved = m
                break
    if resolved is None:
        await interaction.response.send_message(f"Could not resolve target member: {target}. Use a mention, ID, or username#discrim.", ephemeral=True)
        return
    try:
        if image:
            file = await image.to_file()
            await resolved.send(content=message or None, file=file)
        else:
            m = re.search(r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))", message or "", re.IGNORECASE)
            if m:
                url = m.group(1)
                embed = discord.Embed()
                embed.set_image(url=url)
                await resolved.send(content=(message or None), embed=embed)
            else:
                await resolved.send(message or None)
        await interaction.response.send_message(f"Sent DM to {resolved.display_name}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to send DM: {e}", ephemeral=True)


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
    msg = (
        f"Prefix: {cfg.get('prefix')}\n"
        f"Mod role: {cfg.get('mod_role')}\n"
        f"Log channel: {cfg.get('log_channel')}\n"
        f"Welcome channel: {cfg.get('welcome_channel')}"
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


# Website monitoring: alert 'asters.world' by DM when site is down
TARGET_URL = "https://portfolio.aetherassembly.org"
MONITOR_INTERVAL_MINUTES = int(os.getenv("WEBSITE_MONITOR_INTERVAL_MINUTES", "1"))
# Configure notification target: either a guild id/channel id, or fallback behavior
MONITOR_NOTIFY_GUILD_ID = os.getenv("MONITOR_NOTIFY_GUILD_ID")
MONITOR_NOTIFY_CHANNEL_ID = os.getenv("MONITOR_NOTIFY_CHANNEL_ID")
MONITOR_NOTIFY_CHANNEL_NAME = os.getenv("MONITOR_NOTIFY_CHANNEL_NAME", "general")
ASTER_DISPLAY_NAME = os.getenv("ASTER_DISPLAY_NAME", "asters.world")


async def notify_site_down(reason: str):
    """Notify the configured guild/channel if present; otherwise fallback to DMing a named user if found."""
    # Try guild/channel notification first if configured
    if MONITOR_NOTIFY_GUILD_ID:
        try:
            gid = int(MONITOR_NOTIFY_GUILD_ID)
            guild = bot.get_guild(gid)
            if guild:
                # prefer channel id, then channel name
                ch = None
                if MONITOR_NOTIFY_CHANNEL_ID:
                    try:
                        cid = int(MONITOR_NOTIFY_CHANNEL_ID)
                        ch = guild.get_channel(cid) or bot.get_channel(cid)
                    except Exception:
                        ch = None
                if ch is None:
                    ch = discord.utils.get(guild.text_channels, name=MONITOR_NOTIFY_CHANNEL_NAME)
                if ch and ch.permissions_for(guild.me).send_messages:
                    try:
                        await ch.send(f"⚠️ The monitored site {TARGET_URL} appears to be down: {reason}")
                        log(f"Notified guild {guild.id} channel {ch.id} about site down")
                        return
                    except Exception as e:
                        log(f"Failed to send monitor message to guild {guild.id} channel: {e}")
                else:
                    log(f"Monitor: could not find sendable channel in guild {gid}")
            else:
                log(f"Monitor: bot is not in guild {gid}")
        except Exception as e:
            log(f"Monitor notify guild handling error: {e}")

    # Fallback: DM a user with display/name matching ASTER_DISPLAY_NAME
    sent_any = False
    for guild in bot.guilds:
        for member in guild.members:
            if member.name == ASTER_DISPLAY_NAME or member.display_name == ASTER_DISPLAY_NAME:
                try:
                    await member.send(f"⚠️ The monitored site {TARGET_URL} appears to be down: {reason}")
                    log(f"Notified {member} about website down")
                    sent_any = True
                except Exception as e:
                    log(f"Failed to DM {member}: {e}")
    if not sent_any:
        log(f"Could not find member '{ASTER_DISPLAY_NAME}' to DM about site outage; reason: {reason}")


@tasks.loop(minutes=MONITOR_INTERVAL_MINUTES)
async def website_monitor():
    await bot.wait_until_ready()
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(TARGET_URL) as resp:
                status = resp.status
                if status < 200 or status >= 400:
                    await notify_site_down(f"HTTP {status}")
    except Exception as e:
        await notify_site_down(str(e))


@bot.event
async def on_ready():
    log(f'Bot is online as {bot.user}')
    try:
        await bot.tree.sync()
        log("Synced application (slash) commands with Discord")
    except Exception as e:
        log(f"Failed to sync application commands: {e}")
    # start site monitor
    try:
        website_monitor.start()
        log("Started website monitor task")
    except Exception as e:
        log(f"Failed to start website monitor: {e}")


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
