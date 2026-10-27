import asyncio
import ipaddress
import socket
from collections import deque
from dataclasses import asdict, dataclass, replace
from urllib.parse import urlparse
from functools import wraps

import discord
import yt_dlp

from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.exception.music.no_music_playing_exception import NoMusicPlayingException
from libs.exception.music.no_playing_instance_exception import NoPlayingInstanceException
from libs.exception.music.no_result_found_exception import NoResultsFoundException
from libs.exception.music.not_connected_to_voice_channel_exception import NotConnectedToVoiceChannelException
from libs.exception.music.nothing_left_in_back_queue import NothingLeftInBackQueueException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.log import Log
from libs.music.radios import get_radio, radio_choices
from libs.music.stream_audio import StreamingAudio, StreamPlaybackError
from libs.music.diagnostics import music_diagnostic


YOUTUBE_HLS_FORMAT = "bestaudio[protocol^=m3u8]/best[protocol^=m3u8]"


@dataclass(frozen=True)
class Track:
    title: str
    uri: str
    author: str
    length: int
    source: str
    radio_id: str | None = None

    def __str__(self):
        return self.title


def public_url(url):
    """Reject local files and private network destinations before streaming."""
    parsed = urlparse(url)
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username or parsed.password or parsed.port not in (None, 80, 443)):
        raise ValueError(
            "Utilisez une URL HTTP(S) publique, sans identifiants.")
    addresses = socket.getaddrinfo(
        parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError(
            "Les adresses locales et privées ne sont pas autorisées.")
    return url


def publishes_changes(method):
    @wraps(method)
    async def wrapped(self, *args, **kwargs):
        try:
            return await method(self, *args, **kwargs)
        finally:
            if self.on_change:
                self.on_change()
    return wrapped


class MusicManager:
    """Native Discord streaming. yt-dlp only resolves metadata/URLs, never downloads."""

    def __init__(self):
        self.on_change = None
        self.voice_clients = None
        self.back_queue = deque(maxlen=100)
        self._queue = deque()
        self._current = None
        self._lock = asyncio.Lock()
        self._generation = 0
        self.error = None

    @staticmethod
    def _extract(query, *, format_selector="bestaudio/best"):
        with yt_dlp.YoutubeDL({"format": format_selector, "noplaylist": True, "cachedir": False,
                               "quiet": True, "no_warnings": True, "socket_timeout": 15,
                               "retries": 2, "extractor_retries": 2,
                               "js_runtimes": {"node": {}}}) as downloader:
            info = downloader.extract_info(query, download=False)
            if info and "entries" in info:
                info = next(
                    (entry for entry in info["entries"] if entry), None)
            if not info:
                raise NoResultsFoundException
            return info

    @classmethod
    def _search(cls, query, source):
        query = query.strip()
        if not query or len(query) > 500:
            raise ValueError(
                "Recherche vide ou trop longue (500 caractères maximum).")
        if source not in ("youtube", "soundcloud", "radio"):
            raise ValueError("Source inconnue.")
        if source == "radio":
            radio = get_radio(query)
            return Track(radio.name, radio.url, "Radio en direct", 0, "radio", radio.slug)
        if "://" in query:
            parsed = urlparse(query)
            hosts = ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com",
                     "youtu.be") if source == "youtube" else ("soundcloud.com", "www.soundcloud.com")
            if parsed.scheme not in ("http", "https") or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
                raise ValueError(
                    "Le lien doit appartenir à la source sélectionnée.")
        else:
            query = ("ytsearch1:" if source ==
                     "youtube" else "scsearch1:") + query
        info = cls._extract(query)
        uri = ("https://www.youtube.com/watch?v=" +
               info["id"]) if source == "youtube" else info["webpage_url"]
        return Track(info.get("title", "Sans titre"), uri, info.get("uploader") or "Inconnu",
                     int((info.get("duration") or 0) * 1000), source)

    async def search(self, search, source="youtube"):
        # MIWOS caches a thread-affine SQLite connection. Radio lookups must
        # stay on the bot's event-loop thread, just like state/catalogue reads.
        # Only external metadata extraction belongs in the worker pool.
        if source == "radio":
            return self._search(search, source)
        return await asyncio.to_thread(self._search, search, source)

    def authorize(self, member):
        voice = getattr(member, "voice", None)
        if not voice or not voice.channel:
            raise NotConnectedToVoiceChannelException
        if self.voice_clients and self.voice_clients.is_connected() and self.voice_clients.channel.id != voice.channel.id:
            raise ValueError(
                "Rejoignez le salon vocal du Ménestrel pour le contrôler.")
        if not isinstance(voice.channel, discord.VoiceChannel):
            raise ValueError("La musique nécessite un salon vocal classique.")
        permissions = voice.channel.permissions_for(member.guild.me)
        if not (permissions.view_channel and permissions.connect and permissions.speak):
            raise ValueError(
                "Le Ménestrel doit pouvoir voir, rejoindre et parler dans ce salon.")

    async def join(self, voice_state):
        if not voice_state or not voice_state.channel:
            raise NotConnectedToVoiceChannelException
        if not self.voice_clients or not self.voice_clients.is_connected():
            self._halt()
            # Pycord may retain a cached voice client after an interrupted
            # handshake. Reuse a live client, or clean a stale one before joining.
            existing = voice_state.channel.guild.voice_client
            if existing is not None and not existing.is_connected():
                await existing.disconnect(force=True)
                existing = None
            self.voice_clients = existing if existing is not None else await voice_state.channel.connect()
        if self.voice_clients.channel.id != voice_state.channel.id:
            raise ValueError("Rejoignez le salon vocal du Ménestrel.")

    async def _start(self, track):
        # A fresh URL for the same direct format can still return HTTP 403.
        # YouTube may expose a working HLS stream alongside blocked direct audio.
        for attempt in range(2):
            try:
                return await self._start_stream(track, youtube_hls=bool(attempt and track.source == "youtube"))
            except StreamPlaybackError:
                if attempt or track.source == "radio":
                    raise
                if track.source == "youtube":
                    Log.info(
                        "Flux direct YouTube indisponible : tentative du flux HLS.")

    async def _start_stream(self, track, *, youtube_hls=False):
        # Resolve at playback time: expiring stream URLs never enter the queue.
        headers = {}
        if track.source == "radio":
            if track.radio_id:
                radio = get_radio(track.radio_id)
                track = replace(track, title=radio.name, uri=radio.url)
            await asyncio.to_thread(public_url, track.uri)
            stream = track.uri
        else:
            if youtube_hls:
                info = await asyncio.to_thread(self._extract, track.uri, format_selector=YOUTUBE_HLS_FORMAT)
            else:
                info = await asyncio.to_thread(self._extract, track.uri)
            stream = await asyncio.to_thread(public_url, info.get("url", ""))
            headers = info.get("http_headers") or {}
        source = StreamingAudio(stream, headers)
        try:
            await asyncio.wait_for(asyncio.to_thread(source.prepare), timeout=20)
        except BaseException:
            await asyncio.to_thread(source.cleanup)
            raise
        self._generation += 1
        generation = self._generation
        loop = asyncio.get_running_loop()

        def ended(error):
            asyncio.run_coroutine_threadsafe(
                self._finished(generation, error), loop)

        try:
            self.voice_clients.play(source, after=ended)
        except Exception:
            source.cleanup()
            raise
        self._current = track
        self.error = None

    def _halt(self):
        self._generation += 1
        if self.voice_clients:
            self.voice_clients.stop()
        self._current = None

    async def _advance(self, failed=False):
        while self._queue:
            track = self._queue.popleft()
            try:
                await self._start(track)
                return
            except Exception as error:
                failed = True
                self.error = "Impossible de lire un titre. Vérifiez FFmpeg et la disponibilité de la source."
                Log.warning(music_diagnostic(error, "queue/audio startup"))
        if not failed:
            await self._disconnect()

    @publishes_changes
    async def _finished(self, generation, error):
        async with self._lock:
            if generation != self._generation:
                return
            if error:
                self.error = "La lecture audio a été interrompue."
                Log.warning(music_diagnostic(error, "audio playback"))
            if self._current and not error:
                self.back_queue.appendleft(self._current)
            self._current = None
            await self._advance(failed=bool(error))

    @publishes_changes
    async def play(self, voice_state, song):
        async with self._lock:
            await self.join(voice_state)
            if self._current:
                if len(self._queue) >= 100:
                    raise ValueError("La file contient déjà 100 titres.")
                self._queue.append(song)
                raise AlreadyPlayingException
            try:
                await self._start(song)
            except Exception:
                self.error = "Lecture impossible : la source refuse le flux audio ou celui-ci est indisponible."
                raise

    @publishes_changes
    async def skip(self):
        async with self._lock:
            self._require_voice()
            if not self._queue:
                raise NothingLeftInQueueException
            if self._current:
                self.back_queue.appendleft(self._current)
            self._halt()
            await self._advance()

    @publishes_changes
    async def back(self):
        async with self._lock:
            self._require_voice()
            if not self.back_queue:
                raise NothingLeftInBackQueueException
            if self._current and len(self._queue) >= 100:
                raise ValueError(
                    "La file est pleine : impossible de réinsérer le titre actuel.")
            previous = self.back_queue.popleft()
            if self._current:
                self._queue.appendleft(self._current)
            self._queue.appendleft(previous)
            self._halt()
            await self._advance()

    @publishes_changes
    async def pause(self):
        async with self._lock:
            self._require_voice()
            self.voice_clients.pause()

    @publishes_changes
    async def resume(self):
        async with self._lock:
            self._require_voice()
            self.voice_clients.resume()

    async def _disconnect(self):
        self._halt()
        if self.voice_clients:
            await self.voice_clients.disconnect(force=True)
            self.voice_clients = None

    @publishes_changes
    async def stop(self, disconnect=True):
        async with self._lock:
            self._require_voice()
            self._queue.clear()
            self.back_queue.clear()
            self.error = None
            self._halt()
            if disconnect:
                await self._disconnect()

    async def disconnect(self):
        await self.stop()

    def _require_voice(self):
        if not self.voice_clients or not self.voice_clients.is_connected():
            raise NoPlayingInstanceException

    @property
    def is_paused(self):
        self._require_voice()
        return self.voice_clients.is_paused()

    @property
    def now(self):
        self._require_voice()
        if not self._current:
            raise NoMusicPlayingException
        return self._current

    @property
    def queue(self):
        if not self._queue:
            raise NothingLeftInQueueException
        return list(self._queue)

    def state(self):
        connected = bool(
            self.voice_clients and self.voice_clients.is_connected())
        return {"connected": connected, "paused": connected and self.voice_clients.is_paused(),
                "channel_id": str(self.voice_clients.channel.id) if connected else None,
                "channel_name": self.voice_clients.channel.name if connected else None,
                "current": asdict(self._current) if connected and self._current else None,
                "queue": [asdict(track) for track in self._queue],
                "has_previous": bool(self.back_queue), "error": self.error,
                "radios": radio_choices()}
