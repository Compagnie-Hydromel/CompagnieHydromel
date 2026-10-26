import asyncio
import os
from typing import Literal

import aiohttp
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from libs.databases.models.guild import Guild
from libs.utils.http_utils import HTTPUtils


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
    secret = os.getenv("MUSIC_CONTROL_SECRET")
    if not secret:
        raise HTTPException(503, "Le contrôle musical n'est pas configuré.")
    payload = {**command, "guild_id": str(guild.discord_id), "user_id": str(user.discord_id)}
    url = os.getenv("MUSIC_CONTROL_URL", "http://127.0.0.1:8001").rstrip("/") + "/control"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as client:
            async with client.post(url, json=payload, headers={"Authorization": "Bearer " + secret}, allow_redirects=False) as response:
                if response.status not in (200, 400, 403, 404, 503):
                    raise HTTPException(503, "Le Ménestrel est indisponible.")
                result = await response.json()
                if response.status != 200:
                    raise HTTPException(response.status, result.get("detail", "Commande refusée."))
                return result
    except (aiohttp.ClientError, asyncio.TimeoutError):
        raise HTTPException(503, "Le Ménestrel est injoignable. Vérifiez qu'il est démarré.")


@router.get("")
async def show(request: Request, guild_id: int):
    return await forward(request, guild_id, {"action": "state"})


@router.post("")
async def control(request: Request, guild_id: int, command: MusicCommand):
    return await forward(request, guild_id, command.model_dump())
