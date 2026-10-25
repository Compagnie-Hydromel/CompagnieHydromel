from pathlib import Path as FilePath
from typing import Annotated, Literal
from uuid import uuid4
from zoneinfo import available_timezones

from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.datastructures import UploadFile

from libs.databases.models.scheduled_message import ScheduledMessage
from libs.utils.http_utils import HTTPUtils
from libs.utils.upload_utils import image_upload_form


router = APIRouter(prefix="/sessions/guilds/{guild_id}/admin/messages")
ATTACHMENTS = FilePath("storages/locals/scheduled_messages")
MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024


class MessageWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=80)
    channel_id: str = Field(pattern=r"^[1-9][0-9]{0,21}$")
    message: str = Field(max_length=2000)
    day: Literal["daily", "monday", "tuesday", "wednesday",
                 "thursday", "friday", "saturday", "sunday"]
    time: str = Field(pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def valid_schedule(self):
        ScheduledMessage.validate_schedule(self.time, self.timezone)
        return self


async def message_context(request, guild_id):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    discord_guild = guild.get_guild()
    if discord_guild is None or discord_guild.me is None:
        raise HTTPException(
            status_code=503, detail="admin.messages.unavailable")
    return guild, discord_guild


def channel_available(channel, bot):
    permissions = channel.permissions_for(bot)
    return bool(permissions.view_channel and permissions.send_messages)


def message_data(record, discord_guild):
    channel = next((item for item in discord_guild.text_channels if str(
        item.id) == str(record.channel_id)), None)
    return {**{key: getattr(record, key) for key in ("id", "name", "message", "day", "time", "timezone", "last_sent_date", "attachment_name")},
            "channel_id": str(record.channel_id), "channel_name": channel.name if channel else str(record.channel_id),
            "missing_channel": channel is None, "has_attachment": bool(record.attachment_path)}


def find_message(id, guild):
    record = ScheduledMessage.whereFirst(id=id, guild=guild)
    if record is None:
        raise HTTPException(status_code=404, detail="admin.messages.missing")
    return record


def validate_channel(changes, discord_guild):
    channel = next((item for item in discord_guild.text_channels if str(
        item.id) == changes.channel_id), None)
    if channel is None:
        raise HTTPException(
            status_code=404, detail="admin.messages.missingChannel")
    if not channel_available(channel, discord_guild.me):
        raise HTTPException(
            status_code=422, detail="admin.messages.channelPermission")
    return channel


@router.get("")
async def index(request: Request, guild_id: int):
    guild, discord_guild = await message_context(request, guild_id)
    return {"messages": [message_data(record, discord_guild) for record in ScheduledMessage.where(guild=guild)],
            "channels": [{"discord_id": str(channel.id), "name": channel.name,
                          "available": channel_available(channel, discord_guild.me)} for channel in discord_guild.text_channels],
            "timezones": sorted(available_timezones())}


@router.post("", status_code=201)
async def create(request: Request, guild_id: int, changes: MessageWrite):
    guild, discord_guild = await message_context(request, guild_id)
    validate_channel(changes, discord_guild)
    if not changes.message:
        raise HTTPException(
            status_code=422, detail="admin.messages.contentRequired")
    if ScheduledMessage.by_name_and_guild(changes.name, guild) is not None:
        raise HTTPException(status_code=409, detail="admin.messages.duplicate")
    record = ScheduledMessage.createOrFail(guild=guild, **changes.model_dump())
    return message_data(record, discord_guild)


@router.patch("/{message_id}")
async def update(request: Request, guild_id: int, message_id: Annotated[int, Path(gt=0)], changes: MessageWrite):
    guild, discord_guild = await message_context(request, guild_id)
    record = find_message(message_id, guild)
    validate_channel(changes, discord_guild)
    if not changes.message and not record.attachment_path:
        raise HTTPException(
            status_code=422, detail="admin.messages.contentRequired")
    duplicate = ScheduledMessage.by_name_and_guild(changes.name, guild)
    if duplicate is not None and duplicate.id != record.id:
        raise HTTPException(status_code=409, detail="admin.messages.duplicate")
    for key, value in changes.model_dump().items():
        setattr(record, key, value)
    # Preserve last_sent_date so editing does not send the message twice today.
    record.saveOrFail()
    return message_data(record, discord_guild)


@router.delete("/{message_id}")
async def delete(request: Request, guild_id: int, message_id: Annotated[int, Path(gt=0)]):
    guild, _ = await message_context(request, guild_id)
    find_message(message_id, guild).delete()
    # Retain immutable attachments for sends already in progress.
    return {"deleted": True}


@router.post("/{message_id}/attachment")
async def upload_attachment(request: Request, guild_id: int, message_id: Annotated[int, Path(gt=0)]):
    guild, discord_guild = await message_context(request, guild_id)
    record = find_message(message_id, guild)
    channel = next((item for item in discord_guild.text_channels if str(
        item.id) == str(record.channel_id)), None)
    if channel is None or not channel_available(channel, discord_guild.me) or not channel.permissions_for(discord_guild.me).attach_files:
        raise HTTPException(
            status_code=422, detail="admin.messages.attachmentPermission")
    form = await image_upload_form(request, MAX_ATTACHMENT_BYTES, max_fields=0)
    try:
        file = form.get("attachment")
        if len(form.multi_items()) != 1 or not isinstance(file, UploadFile):
            raise HTTPException(
                status_code=422, detail="admin.messages.attachmentRequired")
        content = await file.read(MAX_ATTACHMENT_BYTES + 1)
        if len(content) > MAX_ATTACHMENT_BYTES:
            raise HTTPException(
                status_code=413, detail="admin.messages.tooLarge")
        if not content:
            raise HTTPException(
                status_code=422, detail="admin.messages.attachmentRequired")
        filename = (file.filename or "attachment").replace(
            "\\", "/").rsplit("/", 1)[-1]
        filename = "".join(character for character in filename if character.isprintable())[
            :150] or "attachment"
        ATTACHMENTS.mkdir(parents=True, exist_ok=True)
        path = ATTACHMENTS / uuid4().hex
        previous_path, previous_name = record.attachment_path, record.attachment_name
        created = False
        try:
            with path.open("xb") as destination:
                created = True
                destination.write(content)
            record.attachment_path = "local://scheduled_messages/" + path.name
            record.attachment_name = filename
            record.saveOrFail()
        except Exception:
            record.attachment_path, record.attachment_name = previous_path, previous_name
            if created:
                path.unlink(missing_ok=True)
            raise
        return message_data(record, discord_guild)
    finally:
        await form.close()


@router.delete("/{message_id}/attachment")
async def remove_attachment(request: Request, guild_id: int, message_id: Annotated[int, Path(gt=0)]):
    guild, discord_guild = await message_context(request, guild_id)
    record = find_message(message_id, guild)
    if not record.message:
        raise HTTPException(
            status_code=422, detail="admin.messages.contentRequired")
    record.attachment_path = None
    record.attachment_name = None
    record.saveOrFail()
    return message_data(record, discord_guild)
