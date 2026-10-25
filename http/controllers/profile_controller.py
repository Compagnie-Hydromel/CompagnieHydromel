from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from libs.databases.models.guild_user import GuildUser
from libs.databases.models.profile_layout import ProfileLayout
from libs.databases.models.wallpaper import Wallpaper
from libs.exception.color.color_not_correct_exception import ColorNotCorrectException
from libs.projections.guild_user_projection import GuildUserProjection
from libs.projections.profile_layout_projection import layout_data
from libs.utils.http_utils import HTTPUtils
from libs.utils.utils import Utils
from libs.storages.wallpaper_uploads import WallpaperUploads


router = APIRouter(prefix="/sessions/guilds/{guild_id}/profile")


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name_color: str
    bar_color: str
    wallpaper_id: int | None = Field(default=None, gt=0)
    layout_id: int | None = Field(default=None, gt=0)

    @field_validator("name_color", "bar_color")
    @classmethod
    def valid_color(cls, value):
        try:
            return "#" + Utils.check_color(value)
        except ColorNotCorrectException:
            raise ValueError("Invalid color")


def get_member(request, guild_id):
    user = HTTPUtils.get_user_from_session(request)
    member = GuildUser.whereFirst(user=user, guild_id=guild_id)
    if member is None:
        raise HTTPException(
            status_code=403, detail="Not a member of this guild")
    return member


def profile_data(member):
    owned_ids = {wallpaper.id for wallpaper in member.wallpapers}
    return {
        "user": GuildUserProjection.from_guild_user(member),
        "wallpaper_id": member.wallpaper.id if member.wallpaper else None,
        "layout_id": member.profilelayout.id if member.profilelayout else None,
        "default_wallpaper": Wallpaper.default().url,
        "default_layout": layout_data(ProfileLayout.default()),
        "layouts": [layout_data(layout) for layout in ProfileLayout.available_for_guild(member.guild_id)],
        "wallpapers": [{
            "id": wallpaper.id,
            "name": wallpaper.name,
            "url": WallpaperUploads.public_url(wallpaper.url),
            "price": wallpaper.price,
            "level": wallpaper.level,
            "owned": wallpaper.id in owned_ids,
        } for wallpaper in member.guild.wallpapers],
    }


@router.get("")
async def show(request: Request, guild_id: int):
    return profile_data(get_member(request, guild_id))


@router.patch("")
async def update(request: Request, guild_id: int, changes: ProfileUpdate):
    member = get_member(request, guild_id)
    wallpaper = None
    if changes.wallpaper_id is not None:
        wallpaper = next((item for item in member.wallpapers
                          if item.id == changes.wallpaper_id and item.guild_id == guild_id), None)
        if wallpaper is None:
            raise HTTPException(status_code=403, detail="Wallpaper not owned")

    layout = None
    if changes.layout_id is not None:
        layout = ProfileLayout.find(changes.layout_id)
        if layout is None or layout.guild_id not in (None, guild_id):
            raise HTTPException(status_code=404, detail="Layout not found")

    member.name_color = changes.name_color
    member.bar_color = changes.bar_color
    member.wallpaper = wallpaper
    member.profilelayout = layout
    member.saveOrFail()
    return profile_data(member)


@router.post("/wallpapers/{wallpaper_id}/buy")
async def buy(request: Request, guild_id: int, wallpaper_id: int):
    member = get_member(request, guild_id)
    wallpaper = next((item for item in member.guild.wallpapers
                      if item.id == wallpaper_id), None)
    if wallpaper is None:
        raise HTTPException(status_code=404, detail="Wallpaper not found")
    if any(item.id == wallpaper_id for item in member.wallpapers):
        raise HTTPException(status_code=409, detail="Wallpaper already owned")
    if wallpaper.price <= 0:
        raise HTTPException(status_code=400, detail="Wallpaper is not buyable")
    if member.smartpoint < wallpaper.price:
        raise HTTPException(status_code=400, detail="Not enough smartpoints")

    member.smartpoint -= wallpaper.price
    member.saveOrFail()
    member.wallpapers.append(wallpaper)
    return profile_data(member)
