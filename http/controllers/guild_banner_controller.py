from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile

from libs.databases.models.voice_channels import VoiceChannel
from libs.storages.banner_uploads import BannerUploads
from libs.utils.http_utils import HTTPUtils
from libs.utils.upload_utils import image_upload_form


router = APIRouter(prefix="/sessions/guilds/{guild_id}/admin/banner")


class PositionWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: int = Field(strict=True, ge=0, le=16384)
    y: int = Field(strict=True, ge=0, le=16384)


class ChannelWrite(PositionWrite):
    discord_id: str = Field(pattern=r"^[1-9][0-9]{0,21}$")


def channel_data(record, discord_guild):
    channel = next((item for item in discord_guild.voice_channels if str(
        item.id) == str(record.discord_id)), None)
    return {
        "id": record.id, "discord_id": str(record.discord_id),
        "name": channel.name if channel else str(record.discord_id),
        "missing": channel is None, "x": record.x, "y": record.y,
    }


async def banner_context(request, guild_id):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    discord_guild = guild.get_guild()
    if discord_guild is None:
        raise HTTPException(status_code=503, detail="admin.roles.unavailable")
    return guild, discord_guild


@router.get("")
async def index(request: Request, guild_id: int):
    guild, discord_guild = await banner_context(request, guild_id)
    return {
        "image_url": BannerUploads.public_url(guild.banner_image) if guild.banner_image else None,
        "channels": [channel_data(record, discord_guild) for record in VoiceChannel.where(guild=guild)],
        "available_channels": [{"discord_id": str(channel.id), "name": channel.name,
                                "avatars": [str(member.display_avatar.url) for member in channel.members[:3]]}
                               for channel in discord_guild.voice_channels],
        "can_update_banner": "BANNER" in discord_guild.features and discord_guild.me is not None
                             and discord_guild.me.guild_permissions.manage_guild,
    }


@router.post("/image")
async def upload(request: Request, guild_id: int):
    guild, _ = await banner_context(request, guild_id)
    form = await image_upload_form(request, BannerUploads.MAX_BYTES, max_fields=0)
    try:
        if len(form.multi_items()) != 1 or not isinstance(form.get("image"), UploadFile):
            raise HTTPException(
                status_code=422, detail="One image file is required")
        content = await form["image"].read(BannerUploads.MAX_BYTES + 1)
        url = await run_in_threadpool(BannerUploads.store, content, guild.id)
        try:
            guild.banner_image = url
            guild.saveOrFail()
        except Exception:
            BannerUploads.delete(url)
            raise
        return {"image_url": BannerUploads.public_url(url)}
    finally:
        await form.close()


@router.delete("/image")
async def disable(request: Request, guild_id: int):
    guild, _ = await banner_context(request, guild_id)
    guild.banner_image = None
    guild.saveOrFail()
    return {"image_url": None}


@router.post("/channels", status_code=201)
async def create_channel(request: Request, guild_id: int, changes: ChannelWrite):
    guild, discord_guild = await banner_context(request, guild_id)
    if not any(str(channel.id) == changes.discord_id for channel in discord_guild.voice_channels):
        raise HTTPException(
            status_code=404, detail="admin.banner.missingChannel")
    if VoiceChannel.whereFirst(guild=guild, discord_id=changes.discord_id) is not None:
        raise HTTPException(status_code=409, detail="admin.banner.duplicate")
    record = VoiceChannel.createOrFail(guild=guild, **changes.model_dump())
    return channel_data(record, discord_guild)


@router.patch("/channels/{channel_id}")
async def update_channel(request: Request, guild_id: int, channel_id: Annotated[int, Path(gt=0)], changes: PositionWrite):
    guild, discord_guild = await banner_context(request, guild_id)
    record = VoiceChannel.whereFirst(id=channel_id, guild=guild)
    if record is None:
        raise HTTPException(
            status_code=404, detail="admin.banner.missingChannel")
    record.x, record.y = changes.x, changes.y
    record.saveOrFail()
    return channel_data(record, discord_guild)


@router.delete("/channels/{channel_id}")
async def delete_channel(request: Request, guild_id: int, channel_id: Annotated[int, Path(gt=0)]):
    guild, _ = await banner_context(request, guild_id)
    record = VoiceChannel.whereFirst(id=channel_id, guild=guild)
    if record is None:
        raise HTTPException(
            status_code=404, detail="admin.banner.missingChannel")
    record.delete()
    return {"deleted": True}
