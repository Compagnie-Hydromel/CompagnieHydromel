from datetime import datetime, timezone

import discord
from fastapi import APIRouter, HTTPException, Request

from libs.databases.models.application_model import ApplicationModel
from libs.databases.models.guild import Guild
from libs.utils.http_utils import HTTPUtils


router = APIRouter(prefix="/sessions/guilds/{guild_id}/dashboard")


async def dashboard_context(request, guild_id):
    user = HTTPUtils.get_user_from_session(request)
    guild = Guild.find(guild_id)
    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")
    bot = getattr(ApplicationModel, "bot", None)
    if bot is None or not bot.is_ready():
        raise HTTPException(status_code=503, detail="Discord is not ready")
    discord_guild = guild.get_guild()
    if discord_guild is None or discord_guild.me is None:
        raise HTTPException(status_code=403, detail="Guild is unavailable")
    try:
        member = await discord_guild.fetch_member(int(user.discord_id))
    except (discord.NotFound, discord.Forbidden):
        raise HTTPException(
            status_code=403, detail="Not a member of this guild")
    except discord.HTTPException:
        raise HTTPException(status_code=503, detail="Discord is unavailable")
    return guild, discord_guild, member


def member_identity(member):
    return {"discord_id": str(member.id), "display_name": member.display_name,
            "username": member.name, "avatar_url": str(member.display_avatar.url), "bot": member.bot}


def voice_member(member):
    state = member.voice
    return {**member_identity(member),
            "muted": bool(state and (state.mute or state.self_mute)),
            "deafened": bool(state and (state.deaf or state.self_deaf)),
            "streaming": bool(state and state.self_stream),
            "video": bool(state and state.self_video)}


def leaderboard(records, discord_guild):
    result = []
    for rank, record in enumerate(list(records)[:10], start=1):
        discord_id = str(record.user.discord_id)
        try:
            member = discord_guild.get_member(int(discord_id))
        except ValueError:
            member = None
        identity = member_identity(member) if member else {
            "discord_id": discord_id, "display_name": discord_id,
            "username": discord_id, "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png", "bot": False}
        required = 200 * min(max(record.level, 1), 15)
        result.append({**identity, "rank": rank, "in_guild": member is not None,
                       "level": record.level, "xp": record.point, "xp_required": required,
                       "monthly_xp": record.monthly_point,
                       "progress": max(0, min(1, record.point / required))})
    return result


@router.get("")
async def show(request: Request, guild_id: int):
    guild, discord_guild, viewer = await dashboard_context(request, guild_id)
    channels = []
    all_channels = [(channel, "voice")
                    for channel in discord_guild.voice_channels]
    all_channels += [(channel, "stage")
                     for channel in discord_guild.stage_channels]
    for channel, kind in sorted(all_channels, key=lambda item: item[0].position):
        if not channel.permissions_for(viewer).view_channel or not channel.permissions_for(discord_guild.me).view_channel:
            continue
        members = sorted(channel.members, key=lambda member: (
            member.display_name.casefold(), member.id))
        channels.append({"discord_id": str(channel.id), "name": channel.name, "kind": kind,
                         "category": channel.category.name if channel.category else None,
                         "members": [voice_member(member) for member in members]})
    return {
        "guild": {"id": guild.id, "name": discord_guild.name,
                  "icon_url": str(discord_guild.icon.url) if discord_guild.icon else None},
        "voice_channels": channels,
        "voice_member_count": sum(len(channel["members"]) for channel in channels),
        "active_voice_channel_count": sum(bool(channel["members"]) for channel in channels),
        "monthly_top": leaderboard(guild.get_monthly_top_users(), discord_guild),
        "level_top": leaderboard(guild.get_top_users(), discord_guild),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
