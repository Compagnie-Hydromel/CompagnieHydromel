from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.user import User
from libs.projections.guild_projection import GuildProjection
from libs.projections.guild_user_projection import GuildUserProjection
from libs.projections.user_projection import UserProjection

router = APIRouter(prefix="/sessions")


@router.get("")
async def one(request: Request) -> dict[str, UserProjection]:
    if "authorization" in request.query_params:
        user = User.verify_authorization_token(
            request.query_params["authorization"]
        )
        if not user:
            return RedirectResponse(url="/")
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard")

    user = User.find(request.session.get("user_id", None))
    if not user:
        raise HTTPException(status_code=401, detail="No active session found.")
    return {"user": UserProjection.from_user(user)}


@router.get("/guilds")
async def guilds(request: Request) -> list[GuildProjection]:
    user = User.find(request.session.get("user_id", None))
    if not user:
        raise HTTPException(status_code=401, detail="No active session found.")
    guild_list = []

    for guild_user in user.guildusers:
        guild = GuildProjection.from_guild(guild_user.guild)
        guild_list.append(guild)
    return guild_list


@router.get("/guilds/{guild_id}/user")
async def guild_user(request: Request, guild_id: int) -> GuildUserProjection:
    user = User.find(request.session.get("user_id", None))
    guild = Guild.find(guild_id)

    if not user:
        raise HTTPException(status_code=401, detail="No active session found.")

    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found.")

    guilduser = GuildUser.from_user_and_guild(user, guild)

    return GuildUserProjection.from_guild_user(guilduser)


@router.delete("")
async def delete(request: Request) -> dict[str, str]:
    if not request.session.get("user_id"):
        raise HTTPException(status_code=401, detail="No active session found.")
    request.session.clear()
    return {"message": "Logged out successfully"}
