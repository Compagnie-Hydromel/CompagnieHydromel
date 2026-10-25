import re

import discord
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from libs.utils.http_utils import HTTPUtils


router = APIRouter(prefix="/sessions/guilds/{guild_id}/admin/rules-acceptance")
MESSAGE_ID = re.compile(r"[1-9][0-9]{16,21}")
MESSAGE_LINK = re.compile(
    r"https://(?:(?:canary|ptb)\.)?discord(?:app)?\.com/channels/"
    r"([1-9][0-9]{16,21})/([1-9][0-9]{16,21})/([1-9][0-9]{16,21})/?")


class RulesAcceptanceWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=200)
    emoji: str = Field(min_length=1, max_length=100)

    @field_validator("message")
    @classmethod
    def valid_message(cls, value):
        if not MESSAGE_ID.fullmatch(value) and not MESSAGE_LINK.fullmatch(value):
            raise ValueError("Provide a Discord message ID or message link")
        return value


def acceptance_data(guild):
    message = guild.accepted_rules_message_id
    return {
        "message_discord_id": str(message) if message else None,
        "emoji": guild.accepted_rules_emoji or None,
    }


@router.get("")
async def show(request: Request, guild_id: int):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    return acceptance_data(guild)


@router.patch("")
async def update(request: Request, guild_id: int, changes: RulesAcceptanceWrite):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    message_id = changes.message
    link = MESSAGE_LINK.fullmatch(changes.message)
    if link:
        linked_guild, channel_id, message_id = link.groups()
        if linked_guild != str(guild.discord_id):
            raise HTTPException(
                status_code=422, detail="admin.acceptance.foreignGuild")
        discord_guild = guild.get_guild()
        if discord_guild is None:
            raise HTTPException(
                status_code=503, detail="admin.roles.unavailable")
        channel = discord_guild.get_channel(
            int(channel_id)) or discord_guild.get_thread(int(channel_id))
        if channel is None or not hasattr(channel, "fetch_message"):
            raise HTTPException(
                status_code=404, detail="admin.acceptance.missingMessage")
        try:
            await channel.fetch_message(int(message_id))
        except discord.NotFound:
            raise HTTPException(
                status_code=404, detail="admin.acceptance.missingMessage")
        except discord.Forbidden:
            raise HTTPException(
                status_code=403, detail="admin.acceptance.noAccess")
        except discord.HTTPException:
            raise HTTPException(
                status_code=503, detail="admin.roles.unavailable")

    # Reuse the existing fields consumed by Barman's reaction listener. Changing
    # the message does not reset members who have already accepted the rules.
    guild.accepted_rules_message_id = message_id
    guild.accepted_rules_emoji = changes.emoji
    guild.saveOrFail()
    return acceptance_data(guild)


@router.delete("")
async def disable(request: Request, guild_id: int):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    guild.accepted_rules_message_id = None
    guild.accepted_rules_emoji = None
    guild.saveOrFail()
    return acceptance_data(guild)
