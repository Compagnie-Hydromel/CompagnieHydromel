from typing import Literal

from fastapi import APIRouter, HTTPException, Request, WebSocket
from libs.communication.live import live_updates
from pydantic import BaseModel, ConfigDict, Field

from libs.databases.models.guild import Guild
from libs.utils.http_utils import HTTPUtils
from libs.communication import BusError


router = APIRouter(prefix="/sessions/guilds/{guild_id}/music")


class MusicCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    action: Literal["play", "pause", "resume", "skip", "back", "stop"]
    query: str = Field(default="", max_length=500)
    source: Literal["youtube", "soundcloud", "radio"] = "youtube"


async def forward(request, guild_id, command):
    user = HTTPUtils.get_user_from_session(request)
    guild = Guild.find(guild_id)
    if guild is None:
        raise HTTPException(404, "Guild not found")
    # Membership, visibility and voice permissions are checked by the actual
    # Ménestrel bot, not by the dashboard's separate Discord connection.
    bus = getattr(request.app.state, "component_bus", None)
    if bus is None:
        raise HTTPException(503, "Le bus inter-composants n'est pas configuré.")
    payload = {**command, "guild_id": str(guild.discord_id), "user_id": str(user.discord_id)}
    try:
        return await bus.call("menestrel", "music.control", payload, timeout=90)
    except BusError as error:
        raise HTTPException(error.status, str(error)) from None


@router.get("")
async def show(request: Request, guild_id: int):
    return await forward(request, guild_id, {"action": "state"})


@router.post("")
async def control(request: Request, guild_id: int, command: MusicCommand):
    return await forward(request, guild_id, command.model_dump())


@router.websocket("/live")
async def live(socket: WebSocket, guild_id: int):
    guild = Guild.find(guild_id)
    await live_updates.stream(socket, guild.discord_id if guild else "missing", "music",
                              lambda: show(socket, guild_id))
