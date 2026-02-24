from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.user import User
from libs.projections.guild_projection import GuildProjection
from libs.projections.guild_user_projection import GuildUserProjection
from libs.projections.sessions_projection import SessionsProjection
from libs.projections.user_projection import UserProjection
from libs.utils.http_utils import HTTPUtils

router = APIRouter(prefix="/sessions")


@router.get("")
async def one(request: Request) -> SessionsProjection:
    if "authorization" in request.query_params:
        user = User.verify_authorization_token(
            request.query_params["authorization"]
        )
        if not user:
            return RedirectResponse(url="/")
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard")

    user = HTTPUtils.get_user_from_session(request)
    return SessionsProjection(user=UserProjection.from_user(user))


@router.get("/guilds")
async def guilds(request: Request) -> list[GuildProjection]:
    user = HTTPUtils.get_user_from_session(request)
    guild_list = []

    for guild_user in user.guildusers:
        guild = GuildProjection.from_guild(guild_user.guild)
        guild_list.append(guild)
    return guild_list


@router.get("/guilds/{guild_id}/user")
async def guild_user(request: Request, guild_id: int) -> GuildUserProjection:
    user = HTTPUtils.get_user_from_session(request)
    guild = Guild.findOrFail(guild_id)

    guilduser = GuildUser.from_user_and_guild(user, guild)

    return GuildUserProjection.from_guild_user(guilduser)


@router.delete("")
async def delete(request: Request) -> dict[str, str]:
    HTTPUtils.get_user_from_session(request)
    request.session.clear()
    return {"message": "Logged out successfully"}
