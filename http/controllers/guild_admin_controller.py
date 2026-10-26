import discord
from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, Query, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile

from libs.databases.models.profile_layout import ProfileLayout
from libs.databases.models.wallpaper import Wallpaper
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.user import User
from libs.projections.profile_layout_projection import layout_data
from libs.utils.http_utils import HTTPUtils
from libs.storages.wallpaper_uploads import WallpaperUploads
from libs.utils.upload_utils import image_upload_form


router = APIRouter(prefix="/sessions/guilds/{guild_id}/admin")


class LayoutCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)
    profile_picture_x: int = Field(ge=0, le=372)
    profile_picture_y: int = Field(ge=0, le=153)
    name_x: int = Field(ge=0, le=450)
    name_y: int = Field(ge=0, le=231)
    username_x: int = Field(ge=0, le=450)
    username_y: int = Field(ge=0, le=253)
    level_x: int = Field(ge=0, le=450)
    level_y: int = Field(ge=0, le=241)
    badge_x: int = Field(ge=0, le=468)
    badge_y: int = Field(ge=0, le=249)
    level_bar_x: int = Field(ge=0, le=450)
    level_bar_y: int = Field(ge=0, le=256)


class WallpaperCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)
    price: int = Field(ge=0, le=1000000000)
    level: int = Field(ge=0, le=1000000)


class MemberUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    smartpoint: int = Field(strict=True, ge=0, le=2147483647)
    level: int = Field(strict=True, ge=1, le=1000000)
    xp: int = Field(strict=True, ge=0)

    @model_validator(mode="after")
    def valid_xp(self):
        if self.xp >= 200 * min(self.level, 15):
            raise ValueError("XP must be below the next level threshold")
        return self


def member_data(discord_member, record=None):
    defaults = GuildUser._default_attributes
    level = record.level if record else defaults["level"]
    return {
        "discord_id": str(discord_member.id),
        "display_name": discord_member.display_name,
        "username": discord_member.name,
        "avatar_url": str(discord_member.display_avatar.url),
        "bot": discord_member.bot,
        "smartpoint": record.smartpoint if record else defaults["smartpoint"],
        "level": level,
        "xp": record.point if record else defaults["point"],
        "xp_required": 200 * min(level, 15),
    }


def discord_guild_for(guild):
    discord_guild = guild.get_guild()
    if discord_guild is None:
        raise HTTPException(
            status_code=503, detail="Discord guild is unavailable")
    return discord_guild


def wallpaper_data(wallpaper):
    return {
        **{key: getattr(wallpaper, key) for key in ("id", "name", "price", "level")},
        "url": WallpaperUploads.public_url(wallpaper.url),
    }


async def wallpaper_form(request):
    return await image_upload_form(request, WallpaperUploads.MAX_BYTES, max_fields=3)


@router.get("/access")
async def access(request: Request, guild_id: int):
    await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    return {"administrator": True}


@router.get("")
async def index(request: Request, guild_id: int):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    return {
        "guild_name": guild.name,
        "default_layout": layout_data(ProfileLayout.default()),
        "default_wallpaper": Wallpaper.default().url,
        "layouts": [layout_data(layout) for layout in ProfileLayout.where(guild_id=guild.id)],
        "wallpapers": [wallpaper_data(wallpaper) for wallpaper in guild.wallpapers],
    }


@router.get("/members")
async def members(request: Request, guild_id: int, search: str = Query(default="", max_length=100),
                  page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    discord_guild = discord_guild_for(guild)
    needle = search.strip().casefold()
    matches = sorted((member for member in discord_guild.members if not needle or
                      needle in member.display_name.casefold() or needle in member.name.casefold() or
                      needle in str(member.id)), key=lambda member: (member.display_name.casefold(), member.id))
    page_members = matches[(page - 1) * page_size:page * page_size]
    records = GuildUser.for_discord_ids(
        guild, [member.id for member in page_members])
    result = [member_data(member, records.get(str(member.id)))
              for member in page_members]
    return {"members": result, "total": len(matches), "page": page, "page_size": page_size}


@router.patch("/members/{discord_id}")
async def update_member(request: Request, guild_id: int, discord_id: Annotated[int, Path(gt=0)], changes: MemberUpdate):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    discord_guild = discord_guild_for(guild)
    try:
        member = await discord_guild.fetch_member(discord_id)
    except discord.NotFound:
        raise HTTPException(
            status_code=404, detail="Member not found in this guild")
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Discord access denied")
    except discord.HTTPException:
        raise HTTPException(status_code=503, detail="Discord is unavailable")
    user = User.from_discord_id(str(member.id))
    record = GuildUser.from_user_and_guild(user, guild)
    # Set exact values. Validated XP remains below the threshold, so the model's
    # regular level-up hook does not award money or wallpapers for this edit.
    record.level = changes.level
    record.point = changes.xp
    record.smartpoint = changes.smartpoint
    record.saveOrFail()
    return member_data(member, record)


@router.post("/layouts", status_code=201)
async def create_layout(request: Request, guild_id: int, changes: LayoutCreate):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    if ProfileLayout.whereFirst(guild_id=guild.id, name=changes.name) is not None:
        raise HTTPException(
            status_code=409, detail="Layout name already exists")
    attributes = changes.model_dump()
    attributes["profil_picture_x"] = attributes.pop("profile_picture_x")
    attributes["profil_picture_y"] = attributes.pop("profile_picture_y")
    layout = ProfileLayout.createOrFail(guild=guild, **attributes)
    return layout_data(layout)


@router.post("/wallpapers", status_code=201)
async def create_wallpaper(request: Request, guild_id: int):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    form = await wallpaper_form(request)
    try:
        if len(form.multi_items()) != 4 or set(form) != {"image", "name", "price", "level"}:
            raise HTTPException(
                status_code=422, detail="Provide one image, name, price and level")
        image = form["image"]
        if not isinstance(image, UploadFile):
            raise HTTPException(status_code=422, detail="Image file required")
        try:
            changes = WallpaperCreate.model_validate(
                {key: form[key] for key in ("name", "price", "level")})
        except ValidationError:
            raise HTTPException(
                status_code=422, detail="Invalid wallpaper name, price or level")
        if Wallpaper.whereFirst(guild_id=guild.id, name=changes.name) is not None:
            raise HTTPException(
                status_code=409, detail="Wallpaper name already exists")
        content = await image.read(WallpaperUploads.MAX_BYTES + 1)
        url = await run_in_threadpool(WallpaperUploads.store, content, guild.id)
        try:
            wallpaper = Wallpaper.createOrFail(
                guild=guild, name=changes.name, url=url,
                price=changes.price, level=changes.level)
        except Exception:
            WallpaperUploads.delete(url)
            raise
        return wallpaper_data(wallpaper)
    finally:
        await form.close()


@router.patch("/wallpapers/{wallpaper_id}")
async def update_wallpaper(request: Request, guild_id: int, wallpaper_id: Annotated[int, Path(gt=0)], changes: WallpaperCreate):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    wallpaper = Wallpaper.whereFirst(id=wallpaper_id, guild_id=guild.id)
    if wallpaper is None:
        raise HTTPException(
            status_code=404, detail="Wallpaper not found in this guild")
    duplicate = Wallpaper.whereFirst(name=changes.name, guild_id=guild.id)
    if duplicate is not None and duplicate.id != wallpaper.id:
        raise HTTPException(
            status_code=409, detail="Wallpaper name already exists")
    wallpaper.name = changes.name
    wallpaper.price = changes.price
    wallpaper.level = changes.level
    wallpaper.saveOrFail()
    return wallpaper_data(wallpaper)


@router.post("/wallpapers/{wallpaper_id}/image")
async def replace_wallpaper_image(request: Request, guild_id: int, wallpaper_id: Annotated[int, Path(gt=0)]):
    guild = await HTTPUtils.get_guild_admin_from_session(request, guild_id)
    wallpaper = Wallpaper.whereFirst(id=wallpaper_id, guild_id=guild.id)
    if wallpaper is None:
        raise HTTPException(
            status_code=404, detail="Wallpaper not found in this guild")
    form = await image_upload_form(request, WallpaperUploads.MAX_BYTES, max_fields=0)
    try:
        if len(form.multi_items()) != 1 or not isinstance(form.get("image"), UploadFile):
            raise HTTPException(
                status_code=422, detail="One image file is required")
        content = await form["image"].read(WallpaperUploads.MAX_BYTES + 1)
        url = await run_in_threadpool(WallpaperUploads.store, content, guild.id)
        previous_url = wallpaper.url
        try:
            wallpaper.url = url
            wallpaper.saveOrFail()
        except Exception:
            wallpaper.url = previous_url
            WallpaperUploads.delete(url)
            raise
        # Keep the old immutable image: another request or bot render may still
        # be reading it. The new URL also avoids stale browser/CDN caches.
        return wallpaper_data(wallpaper)
    finally:
        await form.close()
