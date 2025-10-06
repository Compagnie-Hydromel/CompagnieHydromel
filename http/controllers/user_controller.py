from fastapi import APIRouter, Request
from fastapi import HTTPException

from libs.databases.models.user import User
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.guild import Guild

router = APIRouter(prefix="/users")


@router.get("")
async def all(request: Request):
    user = User.all()
    user_list = [u.to_dict() for u in user]
    return user_list


@router.get("/{id}/guilds")
async def guilds(id: int):
    user = User.find(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    guild_list = []

    for guild_user in user.guildusers:
        guild = guild_user.guild
        guild_list.append(guild.to_dict())
    return guild_list
