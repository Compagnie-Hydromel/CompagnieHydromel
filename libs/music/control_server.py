import asyncio
import hmac
import os

import discord
from aiohttp import web

from libs.exception.bot_exception import BotException
from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.log import Log
from libs.music.diagnostics import music_diagnostic, safe_music_error


class MusicControlServer:
    """Private bot RPC. Never publish this port to the internet."""

    def __init__(self, bot, managers):
        self.bot = bot
        self.managers = managers
        self.runner = None
        self.lock = asyncio.Lock()

    async def start(self):
        async with self.lock:
            if self.runner or not os.getenv("MUSIC_CONTROL_SECRET"):
                return
            app = web.Application(client_max_size=4096)
            app.router.add_post("/control", self.control)
            runner = web.AppRunner(app, access_log=None)
            await runner.setup()
            try:
                await web.TCPSite(runner, os.getenv("MUSIC_CONTROL_HOST", "127.0.0.1"),
                                  int(os.getenv("MUSIC_CONTROL_PORT", "8001"))).start()
            except Exception:
                await runner.cleanup()
                raise
            self.runner = runner

    async def close(self):
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        for manager in self.managers.guild.values():
            if manager.voice_clients:
                await manager.disconnect()

    async def control(self, request):
        stage = "request"
        secret = os.getenv("MUSIC_CONTROL_SECRET", "")
        if not secret or not hmac.compare_digest(request.headers.get("Authorization", ""), "Bearer " + secret):
            return web.json_response({"detail": "Unauthorized"}, status=401)
        if not self.bot.is_ready():
            return web.json_response({"detail": "Ménestrel indisponible."}, status=503)
        try:
            data = await request.json()
            if not isinstance(data, dict):
                raise ValueError("Requête invalide.")
            guild = self.bot.get_guild(int(data["guild_id"]))
            if guild is None:
                return web.json_response({"detail": "Le Ménestrel n'est pas sur ce serveur."}, status=404)
            stage = "membership"
            member = await guild.fetch_member(int(data["user_id"]))
            manager = self.managers.get(guild.id)
            action = data.get("action")
            if action == "state":
                stage = "state/catalogue"
                if manager.voice_clients and not manager.voice_clients.channel.permissions_for(member).view_channel:
                    return web.json_response({"detail": "Salon privé."}, status=403)
                return web.json_response(manager.state())
            if action not in ("play", "pause", "resume", "skip", "back", "stop"):
                raise ValueError("Commande inconnue.")
            manager.authorize(member)
            if action == "play":
                query = data.get("query", "")
                if not isinstance(query, str):
                    raise ValueError("Recherche invalide.")
                stage = "source resolution"
                song = await manager.search(query, data.get("source", "youtube"))
                # Voice state may have changed while resolving the stream.
                member = await guild.fetch_member(member.id)
                manager.authorize(member)
                try:
                    stage = "voice connection/audio startup"
                    await manager.play(member.voice, song)
                except AlreadyPlayingException:
                    pass  # Enqueue is a successful web action.
            else:
                stage = "playback control"
                await getattr(manager, action)()
            stage = "state/catalogue"
            return web.json_response(manager.state())
        except (discord.NotFound, discord.Forbidden):
            return web.json_response({"detail": "Accès au serveur refusé."}, status=403)
        except (ValueError, KeyError, TypeError, BotException) as error:
            detail = error.message if isinstance(error, BotException) else str(error)
            return web.json_response({"detail": detail}, status=400)
        except Exception as error:
            Log.warning(music_diagnostic(error, stage))
            if isinstance(error, discord.opus.OpusNotLoaded):
                detail = "Bibliothèque Opus indisponible : installez libopus sur la machine du bot."
            elif isinstance(error, discord.ClientException):
                detail = "Erreur vocale Discord : " + safe_music_error(error)
            elif isinstance(error, asyncio.TimeoutError):
                detail = "Délai dépassé lors de la connexion ou de l'ouverture du flux audio."
            else:
                detail = f"Lecture impossible ({type(error).__name__}, étape : {stage}). Consultez le log du Ménestrel."
            return web.json_response({"detail": detail}, status=503)
