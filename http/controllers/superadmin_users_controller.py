from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Request

from libs.databases.models.user import User
from libs.storages.badge_uploads import BadgeUploads
from libs.utils.http_utils import HTTPUtils


router = APIRouter(prefix="/superadmin/users")


def identity(user):
    bot = getattr(User, "bot", None)
    member = bot.get_user(int(user.discord_id)) if bot else None
    return {"id": user.id, "discord_id": str(user.discord_id),
            "display_name": member.display_name if member else str(user.discord_id),
            "username": member.name if member else None,
            "avatar_url": str(member.display_avatar.url) if member else "https://cdn.discordapp.com/embed/avatars/0.png",
            "is_superadmin": bool(user.is_superadmin)}


@router.get("")
async def index(request: Request, search: str = Query(default="", max_length=100), page: int = Query(default=1, ge=1)):
    HTTPUtils.get_superadmin_from_session(request)
    needle = search.strip().casefold()
    matches = []
    for user in User.all():
        data = identity(user)
        if not needle or any(needle in str(data[key] or "").casefold() for key in ("discord_id", "display_name", "username")):
            matches.append(data)
    matches.sort(key=lambda item: (
        item["display_name"].casefold(), item["id"]))
    return {"users": matches[(page - 1) * 20:page * 20], "total": len(matches), "page": page}


@router.get("/{user_id}")
async def show(request: Request, user_id: Annotated[int, Path(gt=0)]):
    HTTPUtils.get_superadmin_from_session(request)
    user = User.find(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    guilds = []
    bot = getattr(User, "bot", None)
    for record in user.guildusers.withRelations("guild"):
        guild = record.guild
        if guild is None:
            continue
        live_guild = bot.get_guild(int(guild.discord_id)) if bot else None
        cached_member = live_guild.get_member(
            int(user.discord_id)) if live_guild else None
        guilds.append({"id": guild.id, "discord_id": str(guild.discord_id),
                       "name": live_guild.name if live_guild else str(guild.discord_id),
                       "icon_url": str(live_guild.icon.url) if live_guild and live_guild.icon else None,
                       "cached_member": cached_member is not None,
                       "level": record.level, "xp": record.point,
                       "xp_required": 200 * min(max(record.level, 1), 15),
                       "monthly_xp": record.monthly_point, "smartpoint": record.smartpoint,
                       "is_admin": bool(record.is_admin), "has_accepted_rules": bool(record.has_accepted_rules)})
    return {**identity(user), "guilds": guilds,
            "badges": [{"id": badge.id, "name": badge.name, "url": BadgeUploads.public_url(badge.url)} for badge in user.badges]}
