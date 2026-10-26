import asyncio

import discord

from libs.exception.bot_exception import BotException
from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.log import Log
from libs.music.diagnostics import music_diagnostic, safe_music_error
from libs.communication import BusError


class MusicService:
    """Music actions exposed through the shared component bus."""

    def __init__(self, bot, managers):
        self.bot = bot
        self.managers = managers

    async def close(self):
        for manager in self.managers.guild.values():
            if manager.voice_clients and manager.voice_clients.is_connected():
                await manager.disconnect()

    async def control(self, data, context):
        stage = "request"
        if context.caller != "webserver":
            raise BusError("Appel musical refusé.",
                           code="forbidden", status=403)
        if not self.bot.is_ready():
            raise BusError("Ménestrel indisponible.")
        try:
            if not isinstance(data, dict):
                raise ValueError("Requête invalide.")
            guild = self.bot.get_guild(int(data["guild_id"]))
            if guild is None:
                raise BusError(
                    "Le Ménestrel n'est pas sur ce serveur.", code="not_found", status=404)
            stage = "membership"
            member = await guild.fetch_member(int(data["user_id"]))
            manager = self.managers.get(guild.id)
            action = data.get("action")
            if action == "state":
                stage = "state/catalogue"
                if manager.voice_clients and not manager.voice_clients.channel.permissions_for(member).view_channel:
                    raise BusError(
                        "Salon privé.", code="forbidden", status=403)
                return manager.state()
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
            return manager.state()
        except (discord.NotFound, discord.Forbidden):
            raise BusError("Accès au serveur refusé.",
                           code="forbidden", status=403) from None
        except BusError:
            raise
        except (ValueError, KeyError, TypeError, BotException) as error:
            detail = error.message if isinstance(
                error, BotException) else str(error)
            raise BusError(detail, code="invalid", status=400) from None
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
            raise BusError(detail) from None
