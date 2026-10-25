from typing import Annotated, Literal

import discord
from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator

from libs.databases.models.role import Role
from libs.utils.http_utils import HTTPUtils
from libs.utils.role_utils import RoleUtils


router = APIRouter(prefix="/sessions/guilds/{guild_id}/admin/roles")


class RoleWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    discord_id: str = Field(pattern=r"^[1-9][0-9]{0,21}$")
    mode: Literal["level", "reaction"]
    level: int | None = Field(default=None, strict=True, ge=1, le=1000000)
    emoji: str | None = Field(default=None, min_length=1, max_length=100)
    message_discord_id: str | None = Field(
        default=None, pattern=r"^[1-9][0-9]{0,21}$")

    @model_validator(mode="after")
    def valid_mode(self):
        if self.mode == "level":
            if self.level is None:
                raise ValueError("A level is required")
            self.emoji = None
            self.message_discord_id = None
        else:
            if self.emoji is None or self.message_discord_id is None:
                raise ValueError("An emoji and message ID are required")
            self.level = None
        return self


async def role_context(request, guild_id):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    discord_guild = guild.get_guild()
    if discord_guild is None:
        raise HTTPException(status_code=503, detail="admin.roles.unavailable")
    user = HTTPUtils.get_user_from_session(request)
    try:
        roles = await discord_guild.fetch_roles()
        actor = await discord_guild.fetch_member(int(user.discord_id))
    except (discord.Forbidden, discord.NotFound):
        raise HTTPException(status_code=403, detail="admin.denied")
    except discord.HTTPException:
        raise HTTPException(status_code=503, detail="admin.roles.unavailable")
    if not actor.guild_permissions.administrator:
        raise HTTPException(status_code=403, detail="admin.denied")
    return guild, discord_guild, roles, actor


def role_unavailable(role, discord_guild, actor):
    if role.is_default():
        return "admin.roles.defaultRole"
    if role.managed:
        return "admin.roles.managedRole"
    bot = discord_guild.me
    if bot is None or not bot.guild_permissions.manage_roles:
        return "admin.roles.botPermission"
    if role >= bot.top_role:
        return "admin.roles.botHierarchy"
    if actor.id != discord_guild.owner_id and role >= actor.top_role:
        return "admin.roles.actorHierarchy"
    if role.permissions.administrator or role.permissions.manage_roles or role.permissions.manage_guild:
        return "admin.roles.privilegedRole"
    return None


def config_data(record, roles):
    role = next((item for item in roles if str(
        item.id) == str(record.discord_id)), None)
    return {
        "id": record.id,
        "discord_id": str(record.discord_id),
        "name": role.name if role else str(record.discord_id),
        "color": str(role.color) if role else "#999999",
        "missing": role is None,
        "mode": "level" if record.level is not None else "reaction",
        "level": record.level,
        "emoji": record.emoji,
        "message_discord_id": record.message_discord_id,
    }


def validate_rule(changes, guild, discord_guild, roles, actor, current=None):
    role = next((item for item in roles if str(
        item.id) == changes.discord_id), None)
    if role is None:
        raise HTTPException(status_code=404, detail="admin.roles.missingRole")
    reason = role_unavailable(role, discord_guild, actor)
    if reason:
        raise HTTPException(status_code=422, detail=reason)
    duplicate = Role.whereFirst(guild=guild, discord_id=changes.discord_id)
    if duplicate is not None and (current is None or duplicate.id != current.id):
        raise HTTPException(
            status_code=409, detail="admin.roles.duplicateRole")
    if changes.level is not None:
        duplicate = Role.whereFirst(guild=guild, level=changes.level)
        if duplicate is not None and (current is None or duplicate.id != current.id):
            raise HTTPException(
                status_code=409, detail="admin.roles.duplicateLevel")
    return role


@router.get("")
async def index(request: Request, guild_id: int):
    guild, discord_guild, roles, actor = await role_context(request, guild_id)
    return {
        "roles": [{"discord_id": str(role.id), "name": role.name, "color": str(role.color),
                   "unavailable": role_unavailable(role, discord_guild, actor)} for role in reversed(roles)],
        "rules": [config_data(record, roles) for record in Role.where(guild=guild)],
    }


@router.post("", status_code=201)
async def create(request: Request, guild_id: int, changes: RoleWrite):
    guild, discord_guild, roles, actor = await role_context(request, guild_id)
    validate_rule(changes, guild, discord_guild, roles, actor)
    record = Role.createOrFail(guild=guild, discord_id=changes.discord_id,
                               level=changes.level, emoji=changes.emoji, message_discord_id=changes.message_discord_id)
    sync = await RoleUtils.update_all_user_role(discord_guild) if changes.level is not None else None
    return {"rule": config_data(record, roles), "sync": sync}


@router.patch("/{rule_id}")
async def update(request: Request, guild_id: int, rule_id: Annotated[int, Path(gt=0)], changes: RoleWrite):
    guild, discord_guild, roles, actor = await role_context(request, guild_id)
    record = Role.whereFirst(id=rule_id, guild=guild)
    if record is None:
        raise HTTPException(status_code=404, detail="admin.roles.missingRule")
    validate_rule(changes, guild, discord_guild, roles, actor, current=record)
    old_level = record.level
    removed = [role for role in roles if str(role.id) == str(record.discord_id)
               and old_level is not None and (changes.level is None or changes.discord_id != str(record.discord_id))]
    record.discord_id = changes.discord_id
    record.level = changes.level
    record.emoji = changes.emoji
    record.message_discord_id = changes.message_discord_id
    record.saveOrFail()
    sync = await RoleUtils.update_all_user_role(discord_guild, removed_roles=removed) if old_level is not None or changes.level is not None else None
    return {"rule": config_data(record, roles), "sync": sync}


@router.delete("/{rule_id}")
async def delete(request: Request, guild_id: int, rule_id: Annotated[int, Path(gt=0)]):
    guild, discord_guild, roles, _ = await role_context(request, guild_id)
    record = Role.whereFirst(id=rule_id, guild=guild)
    if record is None:
        raise HTTPException(status_code=404, detail="admin.roles.missingRule")
    is_level = record.level is not None
    removed = [role for role in roles if str(role.id) == str(
        record.discord_id)] if is_level else []
    record.delete()
    sync = await RoleUtils.update_all_user_role(discord_guild, removed_roles=removed) if is_level else None
    return {"sync": sync}


@router.post("/sync")
async def sync(request: Request, guild_id: int):
    _, discord_guild, _, _ = await role_context(request, guild_id)
    return await RoleUtils.update_all_user_role(discord_guild)
