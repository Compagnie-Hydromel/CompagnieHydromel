import asyncio
import io
import shlex
import sqlite3
import threading
import shutil
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord
from aiohttp import web
from aiohttp.test_utils import TestServer

from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.music.service import MusicService
from libs.communication import BusError
from tests.bus_support import BusHarness
from libs.music.guild_music_manager import GuildMusicManager
from libs.music.music_manager import MusicManager, Track, YOUTUBE_HLS_FORMAT, public_url
from libs.music.music_player_displayer import MusicPlayerDisplayer
from libs.music.radios import DEFAULT_RADIOS as RADIOS, RadioStation, radio_choices
from libs.music.stream_audio import StreamingAudio, StreamPlaybackError, stream_options
from libs.music.diagnostics import music_diagnostic
from libs.utils.utils import Utils


controller = Utils.import_module_from_path("music_controller", "http/controllers/music_controller.py")


def track(name="Song", source="youtube"):
    return Track(name, "https://www.youtube.com/watch?v=123", "Artist", 123000, source)


def mock_catalog(test):
    records = [SimpleNamespace(id=index + 1, slug=radio.id, name=radio.name, url=radio.url)
               for index, radio in enumerate(RADIOS)]
    for target, kwargs in (("all", {"return_value": records}),
                           ("whereFirst", {"side_effect": lambda **values: next((radio for radio in records if radio.slug == values["slug"]), None)})):
        mock = patch.object(RadioStation, target, **kwargs)
        mock.start()
        test.addCleanup(mock.stop)
    return records


class TestMusicManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.radios = mock_catalog(self)
        self.manager = MusicManager()
        self.voice = Mock()
        self.voice.is_connected.return_value = True
        self.voice.is_paused.return_value = False
        self.voice.disconnect = AsyncMock()
        self.voice.channel.id = 100
        self.voice.channel.name = "Tavern"
        self.manager.voice_clients = self.voice
        self.state = SimpleNamespace(channel=self.voice.channel)

    async def fake_start(self, song):
        self.manager._generation += 1
        self.manager._current = song

    async def test_enqueue_while_paused_does_not_restart(self):
        self.manager._current = track("First")
        self.voice.is_paused.return_value = True
        with self.assertRaises(AlreadyPlayingException):
            await self.manager.play(self.state, track("Second"))
        self.assertEqual(self.manager.queue[0].title, "Second")
        self.voice.play.assert_not_called()
        self.assertTrue(self.manager.state()["paused"])

    async def test_skip_back_and_stale_callbacks(self):
        self.manager._current = track("First")
        self.manager._queue.append(track("Second"))
        with patch.object(self.manager, "_start", side_effect=self.fake_start):
            await self.manager.skip()
            self.assertEqual(self.manager.now.title, "Second")
            await self.manager._finished(0, None)
            self.assertEqual(self.manager.now.title, "Second")
            await self.manager.back()
            self.assertEqual(self.manager.now.title, "First")
            self.assertEqual(self.manager.queue[0].title, "Second")

    async def test_natural_end_advances_then_disconnects(self):
        self.manager._current = track("First")
        self.manager._queue.append(track("Second"))
        with patch.object(self.manager, "_start", side_effect=self.fake_start):
            await self.manager._finished(0, None)
            self.assertEqual(self.manager.now.title, "Second")
            await self.manager._finished(self.manager._generation, None)
        self.voice.disconnect.assert_awaited_once()
        self.assertFalse(self.manager.state()["connected"])

    async def test_failed_track_is_skipped(self):
        self.manager._queue.extend([track("Broken"), track("Good")])

        async def start(song):
            if song.title == "Broken":
                raise ValueError("Unavailable")
            await self.fake_start(song)

        with patch.object(self.manager, "_start", side_effect=start), patch("libs.music.music_manager.Log.warning"):
            await self.manager._advance()
        self.assertEqual(self.manager.now.title, "Good")

    async def test_stop_clears_queue_and_history(self):
        self.manager._current = track()
        self.manager._queue.append(track())
        self.manager.back_queue.append(track())
        await self.manager.stop()
        self.assertEqual(self.manager.state()["queue"], [])
        self.assertFalse(self.manager.back_queue)
        self.assertIsNone(self.manager.voice_clients)

    async def test_skip_empty_queue_preserves_current(self):
        self.manager._current = track()
        with self.assertRaises(NothingLeftInQueueException):
            await self.manager.skip()
        self.assertIsNotNone(self.manager.now)

    async def test_queue_limit(self):
        self.manager._current = track()
        self.manager._queue.extend([track()] * 100)
        with self.assertRaises(ValueError):
            await self.manager.play(self.state, track())

    async def test_reuses_existing_live_voice_client_without_reconnecting(self):
        self.manager.voice_clients = None
        channel = SimpleNamespace(id=100, guild=SimpleNamespace(voice_client=self.voice), connect=AsyncMock())
        await self.manager.join(SimpleNamespace(channel=channel))
        self.assertIs(self.manager.voice_clients, self.voice)
        channel.connect.assert_not_awaited()

    async def test_cleans_stale_cached_voice_connection_before_reconnecting(self):
        stale = Mock(is_connected=Mock(return_value=False), disconnect=AsyncMock())
        self.manager.voice_clients = stale
        channel = SimpleNamespace(id=100, guild=SimpleNamespace(voice_client=stale), connect=AsyncMock(return_value=self.voice))
        await self.manager.join(SimpleNamespace(channel=channel))
        stale.disconnect.assert_awaited_once_with(force=True)
        channel.connect.assert_awaited_once()
        self.assertIs(self.manager.voice_clients, self.voice)

    async def test_sources_resolve_metadata_without_downloading(self):
        info = {"id": "123", "title": "Title", "duration": 12, "webpage_url": "https://soundcloud.com/artist/song"}
        downloader = Mock()
        downloader.extract_info.return_value = info
        with patch("libs.music.music_manager.yt_dlp.YoutubeDL") as factory:
            factory.return_value.__enter__.return_value = downloader
            song = await self.manager.search("title", "soundcloud")
            downloader.extract_info.assert_called_once_with("scsearch1:title", download=False)
            self.assertEqual(song.source, "soundcloud")
            self.assertEqual(song.length, 12000)

    async def test_radio_uses_predefined_catalogue_without_extraction(self):
        with patch.object(self.manager, "_extract") as extract:
            for radio in RADIOS:
                song = await self.manager.search(radio.id, "radio")
                self.assertEqual(song.source, "radio")
                self.assertEqual(song.length, 0)
                self.assertEqual(song.title, radio.name)
                self.assertEqual(song.uri, radio.url)
            extract.assert_not_called()

    async def test_radio_lookup_uses_sqlite_on_connection_owner_thread(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("CREATE TABLE radios (slug TEXT, name TEXT, url TEXT)")
        connection.execute("INSERT INTO radios VALUES (?, ?, ?)", ("fip", "FIP", RADIOS[0].url))
        owner = threading.get_ident()

        def lookup(slug):
            self.assertEqual(threading.get_ident(), owner)
            row = connection.execute("SELECT slug, name, url FROM radios WHERE slug = ?", (slug,)).fetchone()
            return SimpleNamespace(slug=row[0], name=row[1], url=row[2])

        with patch("libs.music.music_manager.get_radio", side_effect=lookup):
            songs = await asyncio.gather(*(self.manager.search("fip", "radio") for _ in range(3)))
        self.assertEqual([song.title for song in songs], ["FIP"] * 3)

    async def test_external_metadata_extraction_still_runs_outside_event_loop(self):
        owner = threading.get_ident()
        workers = []

        def extract(query):
            workers.append(threading.get_ident())
            return {"id": "123", "title": "Title", "webpage_url": "https://soundcloud.com/artist/song"}

        with patch.object(MusicManager, "_extract", side_effect=extract):
            await self.manager.search("title", "youtube")
            await self.manager.search("title", "soundcloud")
        self.assertEqual(len(workers), 2)
        self.assertTrue(all(worker != owner for worker in workers))

    async def test_radio_rejects_unknown_ids_and_all_user_urls(self):
        with patch.dict("os.environ", {"MUSIC_RADIO_URLS": RADIOS[0].url}), patch.object(self.manager, "_extract") as extract:
            for query in ("unknown", RADIOS[0].url, "https://radio.example/live.mp3", "http://127.0.0.1/stream"):
                with self.assertRaises(ValueError):
                    await self.manager.search(query, "radio")
            extract.assert_not_called()

    async def test_state_exposes_named_radio_choices_not_stream_urls(self):
        choices = self.manager.state()["radios"]
        self.assertEqual(choices, radio_choices())
        self.assertEqual(len({radio["id"] for radio in choices}), len(RADIOS))
        self.assertTrue(all(set(radio) == {"id", "name"} for radio in choices))

    async def test_arbitrary_urls_are_not_sent_to_extractor(self):
        with patch.object(self.manager, "_extract") as extract:
            for url in ("http://127.0.0.1/secret", "file:///etc/passwd", "https://youtube.com.evil.test/watch", "https://youtube.com@evil.test/watch"):
                with self.assertRaises(ValueError):
                    await self.manager.search(url)
            extract.assert_not_called()

    async def test_ffmpeg_streams_resolved_url_and_reresolves_each_play(self):
        with patch.object(self.manager, "_extract", return_value={"url": "https://cdn.example/audio"}) as extract, patch(
            "libs.music.music_manager.public_url", side_effect=lambda url: url
        ), patch("libs.music.music_manager.StreamingAudio") as ffmpeg:
            await self.manager._start(track())
            await self.manager._start(track())
            self.assertEqual(extract.call_count, 2)
            self.assertEqual(ffmpeg.call_args.args, ("https://cdn.example/audio", {}))
            self.assertEqual(ffmpeg.return_value.prepare.call_count, 2)
            self.assertEqual(self.voice.play.call_count, 2)

    async def test_stream_headers_are_forwarded_and_initial_failure_is_retried(self):
        headers = {"User-Agent": "yt-dlp agent", "Referer": "https://www.youtube.com/"}
        with patch.object(self.manager, "_extract", return_value={"url": "https://cdn.example/audio", "http_headers": headers}) as extract, patch(
            "libs.music.music_manager.public_url", side_effect=lambda url: url
        ), patch("libs.music.music_manager.StreamingAudio") as ffmpeg, patch("libs.music.music_manager.Log.info"):
            broken, good = Mock(), Mock()
            broken.prepare.side_effect = StreamPlaybackError()
            ffmpeg.side_effect = [broken, good]
            await self.manager._start(track())
        self.assertEqual(extract.call_count, 2)
        self.assertEqual(extract.call_args.kwargs, {"format_selector": YOUTUBE_HLS_FORMAT})
        self.assertEqual(ffmpeg.call_args.args[1], headers)
        broken.cleanup.assert_called_once()
        self.voice.play.assert_called_once_with(good, after=unittest.mock.ANY)

    async def test_youtube_hls_selector_only_applies_to_failed_direct_playback(self):
        with patch.object(self.manager, "_start_stream", new_callable=AsyncMock) as start:
            await self.manager._start(track())
            start.assert_awaited_once_with(track(), youtube_hls=False)

    async def test_youtube_hls_failure_has_no_unbounded_retries(self):
        with patch.object(self.manager, "_start_stream", new_callable=AsyncMock, side_effect=StreamPlaybackError()) as start, patch("libs.music.music_manager.Log.info"):
            with self.assertRaises(StreamPlaybackError):
                await self.manager._start(track())
        self.assertEqual(start.await_count, 2)
        self.assertTrue(start.call_args.kwargs["youtube_hls"])

    async def test_soundcloud_retry_does_not_use_youtube_hls_selector(self):
        with patch.object(self.manager, "_start_stream", new_callable=AsyncMock, side_effect=[StreamPlaybackError(), None]) as start:
            await self.manager._start(track(source="soundcloud"))
        self.assertEqual(start.await_count, 2)
        self.assertFalse(start.call_args.kwargs["youtube_hls"])

    async def test_extractor_accepts_hls_selector_without_downloading(self):
        with patch("libs.music.music_manager.yt_dlp.YoutubeDL") as factory:
            factory.return_value.__enter__.return_value.extract_info.return_value = {"id": "123"}
            MusicManager._extract("https://www.youtube.com/watch?v=123", format_selector=YOUTUBE_HLS_FORMAT)
        self.assertEqual(factory.call_args.args[0]["format"], YOUTUBE_HLS_FORMAT)
        factory.return_value.__enter__.return_value.extract_info.assert_called_once_with("https://www.youtube.com/watch?v=123", download=False)

    async def test_failed_skip_does_not_disconnect_and_exposes_error(self):
        self.manager._current = track("First")
        self.manager._queue.append(track("Forbidden"))
        with patch.object(self.manager, "_start", side_effect=StreamPlaybackError()), patch("libs.music.music_manager.Log.warning"):
            await self.manager.skip()
        self.voice.disconnect.assert_not_awaited()
        self.assertTrue(self.manager.state()["connected"])
        self.assertIsNone(self.manager.state()["current"])
        self.assertTrue(self.manager.state()["error"])

    async def test_runtime_decoder_error_is_not_a_normal_end(self):
        self.manager._current = track()
        with patch("libs.music.music_manager.Log.warning"):
            await self.manager._finished(0, StreamPlaybackError())
        self.voice.disconnect.assert_not_awaited()
        self.assertTrue(self.manager.state()["error"])
        self.assertFalse(self.manager.back_queue)

    async def test_deleted_radio_is_not_played_from_an_old_queue_entry(self):
        song = await self.manager.search("fip", "radio")
        with patch.object(RadioStation, "whereFirst", return_value=None), patch("libs.music.music_manager.StreamingAudio") as ffmpeg:
            with self.assertRaises(ValueError):
                await self.manager._start(song)
        ffmpeg.assert_not_called()

    async def test_radio_choices_follow_database_changes_without_restart(self):
        self.radios.append(SimpleNamespace(id=7, slug="new-radio", name="New Radio", url="https://example.com/live"))
        self.assertIn({"id": "new-radio", "name": "New Radio"}, self.manager.state()["radios"])
        self.assertEqual((await self.manager.search("new-radio", "radio")).title, "New Radio")

    async def test_managers_are_isolated_per_guild_and_instance(self):
        first, second = GuildMusicManager(), GuildMusicManager()
        self.assertIs(first.get(1), first.get(1))
        self.assertIsNot(first.get(1), first.get(2))
        self.assertIsNot(first.get(1), second.get(1))

    async def test_discord_buttons_defer_before_stream_resolution(self):
        self.manager._current = track()
        interaction = SimpleNamespace(response=SimpleNamespace(defer=AsyncMock()),
                                      edit_original_response=AsyncMock(), followup=SimpleNamespace(send=AsyncMock()))

        async def skip():
            interaction.response.defer.assert_awaited_once()

        self.manager.skip = AsyncMock(side_effect=skip)
        view = MusicPlayerDisplayer(self.manager)
        await view._control(interaction, "skip")
        self.manager.skip.assert_awaited_once()
        interaction.edit_original_response.assert_awaited_once()

    async def test_discord_button_rejects_listener_outside_voice_channel(self):
        view = MusicPlayerDisplayer(self.manager)
        interaction = SimpleNamespace(user=SimpleNamespace(voice=None),
                                      response=SimpleNamespace(send_message=AsyncMock()))
        self.assertFalse(await view.interaction_check(interaction))
        interaction.response.send_message.assert_awaited_once()

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is not installed")
    async def test_real_ffmpeg_streams_http_audio_into_discord_pcm_without_files(self):
        audio = io.BytesIO()
        with wave.open(audio, "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(48000)
            wav.writeframes(b"\x00" * 48000)

        async def stream(request):
            return web.Response(body=audio.getvalue(), content_type="audio/wav")

        app = web.Application()
        app.router.add_get("/live.wav", stream)
        async with TestServer(app) as server:
            with patch("libs.music.music_manager.public_url", side_effect=lambda url: url):
                await self.manager._start(Track("Radio", str(server.make_url("/live.wav")), "Radio", 0, "radio"))
            source = self.voice.play.call_args.args[0]
            try:
                self.assertIsNone(source._pipe_reader_thread)
                pcm = await asyncio.wait_for(asyncio.to_thread(source.read), timeout=10)
                self.assertEqual(len(pcm), 3840)  # 20 ms of stereo 48 kHz PCM.
            finally:
                await asyncio.to_thread(source.cleanup)
            self.assertTrue(source._error_sink.closed)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is not installed")
    async def test_real_http_403_fails_before_reporting_playback_and_keeps_voice(self):
        from aiohttp import web

        async def forbidden(request):
            return web.Response(status=403)

        app = web.Application()
        app.router.add_get("/blocked", forbidden)
        async with TestServer(app) as server:
            with patch("libs.music.music_manager.public_url", side_effect=lambda url: url), self.assertRaises(StreamPlaybackError):
                await self.manager.play(self.state, Track("Blocked", str(server.make_url("/blocked")), "Radio", 0, "radio"))
        self.voice.play.assert_not_called()
        self.voice.disconnect.assert_not_awaited()
        self.assertTrue(self.manager.state()["error"])

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is not installed")
    async def test_real_ffmpeg_receives_extractor_headers(self):
        from aiohttp import web
        audio = io.BytesIO()
        with wave.open(audio, "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(48000)
            wav.writeframes(b"\x00" * 48000)
        received = []

        async def protected(request):
            received.append(request.headers.get("User-Agent"))
            if request.headers.get("User-Agent") != "expected-agent" or request.headers.get("Referer") != "https://www.youtube.com/":
                return web.Response(status=403)
            return web.Response(body=audio.getvalue(), content_type="audio/wav")

        app = web.Application()
        app.router.add_get("/audio", protected)
        async with TestServer(app) as server:
            with patch("libs.music.music_manager.public_url", side_effect=lambda url: url), patch.object(
                self.manager, "_extract", return_value={"url": str(server.make_url("/audio")), "http_headers": {"User-Agent": "expected-agent", "Referer": "https://www.youtube.com/"}}
            ):
                await self.manager._start(track())
            source = self.voice.play.call_args.args[0]
            try:
                self.assertEqual(len(source.read()), 3840)
                self.assertEqual(received, ["expected-agent"])
            finally:
                await asyncio.to_thread(source.cleanup)


class TestMusicAccess(unittest.TestCase):
    def test_diagnostics_include_failure_type_and_stage_but_redact_secrets(self):
        with patch.dict("os.environ", {"MENESTREL_TOKEN": "token-to-hide"}):
            diagnostic = music_diagnostic(RuntimeError("failed https://cdn.example/audio?sig=signed-secret token-to-hide\nCookie: session=private-cookie"), "audio startup")
        self.assertIn("RuntimeError", diagnostic)
        self.assertIn("audio startup", diagnostic)
        for secret in ("signed-secret", "token-to-hide", "private-cookie", "cdn.example"):
            self.assertNotIn(secret, diagnostic)

    def test_ffmpeg_nonzero_exit_after_start_raises_instead_of_signalling_normal_end(self):
        with patch.object(discord.FFmpegPCMAudio, "__init__", return_value=None), patch.object(discord.FFmpegPCMAudio, "read", return_value=b""):
            source = StreamingAudio("https://example.com/audio", {})
            source._process = Mock()
            source._process.wait.return_value = 1
            try:
                with self.assertRaises(StreamPlaybackError):
                    source.read()
                source._process.wait.return_value = 0
                self.assertEqual(source.read(), b"")
            finally:
                source.cleanup()

    def test_http_header_values_cannot_inject_options_or_extra_headers(self):
        options = shlex.split(stream_options({"User-Agent": 'agent " -i bad', "Referer": "good\r\nBad: injected", "Bad\nName": "bad"}))
        self.assertEqual(options[-2], "-headers")
        self.assertEqual(options[-1], 'User-Agent: agent " -i bad\r\n')
        self.assertNotIn("-i", options)

    def test_requires_same_voice_channel_and_bot_permissions(self):
        manager = MusicManager()
        channel = Mock(spec=discord.VoiceChannel)
        channel.id = 100
        channel.permissions_for.return_value = SimpleNamespace(view_channel=True, connect=True, speak=True)
        member = SimpleNamespace(voice=SimpleNamespace(channel=channel), guild=SimpleNamespace(me=Mock()))
        manager.authorize(member)
        manager.voice_clients = Mock(channel=SimpleNamespace(id=200))
        with self.assertRaises(ValueError):
            manager.authorize(member)
        manager.voice_clients = None
        channel.permissions_for.return_value.speak = False
        with self.assertRaises(ValueError):
            manager.authorize(member)

    def test_private_network_streams_are_rejected(self):
        for address in ("127.0.0.1", "10.0.0.1", "169.254.169.254", "::1"):
            with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", (address, 443))]), self.assertRaises(ValueError):
                public_url("https://example.com/audio")


class TestMusicControl(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        mock_catalog(self)
        from aiohttp import web
        self.manager = Mock()
        self.manager.state.return_value = {"connected": False, "queue": []}
        self.manager.search = AsyncMock(return_value=track())
        self.manager.play = AsyncMock()
        self.manager.pause = AsyncMock()
        self.manager.voice_clients = None
        self.member = SimpleNamespace(id=42, voice=Mock())
        self.guild = SimpleNamespace(id=123, fetch_member=AsyncMock(return_value=self.member))
        self.bot = Mock()
        self.bot.get_guild.return_value = self.guild
        self.managers = Mock()
        self.managers.get.return_value = self.manager
        service = MusicService(self.bot, self.managers)
        self.harness = await BusHarness().start()
        self.music_bus = self.harness.client("menestrel")
        self.music_bus.register("music.control", service.control, callers={"webserver"})
        self.web_bus = self.harness.client("webserver")
        await self.harness.connect(self.music_bus, self.web_bus)
        self.request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(component_bus=self.web_bus)))

    async def asyncTearDown(self):
        await self.harness.close()

    async def post(self, **changes):
        try:
            result = await self.web_bus.call("menestrel", "music.control", {"guild_id": "123", "user_id": "42", "action": "pause", **changes})
            return SimpleNamespace(status=200, data=result)
        except BusError as error:
            return SimpleNamespace(status=error.status)

    async def test_rpc_requires_secret(self):
        import aiohttp
        async with aiohttp.ClientSession() as client:
            with self.assertRaises(aiohttp.WSServerHandshakeError) as error:
                await client.ws_connect(self.harness.url, headers={"X-Component": "webserver", "Authorization": "Bearer wrong"})
        self.assertEqual(error.exception.status, 403)
        self.bot.get_guild.assert_not_called()

    async def test_controls_authorize_actual_member(self):
        response = await self.post()
        self.assertEqual(response.status, 200)
        self.guild.fetch_member.assert_awaited_once_with(42)
        self.manager.authorize.assert_called_once_with(self.member)
        self.manager.pause.assert_awaited_once()

    async def test_denied_member_cannot_start_extraction(self):
        self.manager.authorize.side_effect = ValueError("Wrong voice channel")
        response = await self.post(action="play", query="song")
        self.assertEqual(response.status, 400)
        self.manager.search.assert_not_awaited()

    async def test_enqueue_is_success_and_voice_is_rechecked(self):
        self.manager.play.side_effect = AlreadyPlayingException()
        response = await self.post(action="play", query="song", source="soundcloud")
        self.assertEqual(response.status, 200)
        self.manager.search.assert_awaited_once_with("song", "soundcloud")
        self.assertEqual(self.manager.authorize.call_count, 2)

    async def test_private_channel_hides_current_and_queue(self):
        self.manager.voice_clients = Mock()
        self.manager.voice_clients.channel.permissions_for.return_value.view_channel = False
        response = await self.post(action="state")
        self.assertEqual(response.status, 403)
        self.manager.state.assert_not_called()

    async def test_non_member_cannot_read_state(self):
        self.guild.fetch_member.side_effect = discord.NotFound(SimpleNamespace(status=404, reason="Not found"), "Not found")
        response = await self.post(action="state")
        self.assertEqual(response.status, 403)

    async def test_web_proxy_uses_session_identity_and_discord_guild_id(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session", return_value=SimpleNamespace(discord_id="42")), patch.object(
            controller.Guild, "find", return_value=SimpleNamespace(discord_id="123")
        ):
            result = await controller.control(self.request, 7, controller.MusicCommand(action="pause"))
        self.assertEqual(result["queue"], [])
        self.bot.get_guild.assert_called_with(123)
        self.guild.fetch_member.assert_awaited_once_with(42)

    async def test_web_proxy_requires_session_before_rpc(self):
        from fastapi import HTTPException
        with patch.object(controller.HTTPUtils, "get_user_from_session", side_effect=HTTPException(401)), self.assertRaises(HTTPException):
            await controller.show(Mock(), 7)
        self.bot.get_guild.assert_not_called()

    async def test_unexpected_stream_error_is_logged_with_stage_and_forwarded_to_web(self):
        from fastapi import HTTPException
        self.manager.play.side_effect = RuntimeError("Failure in voice connection")
        with patch.object(controller.HTTPUtils, "get_user_from_session", return_value=SimpleNamespace(discord_id="42")), patch.object(
            controller.Guild, "find", return_value=SimpleNamespace(discord_id="123")
        ), patch("libs.music.service.Log.warning") as log, self.assertRaises(HTTPException) as error:
            await controller.control(self.request, 7, controller.MusicCommand(action="play", query="test"))
        self.assertEqual(error.exception.status_code, 503)
        self.assertIn("RuntimeError", error.exception.detail)
        self.assertIn("voice connection/audio startup", error.exception.detail)
        self.assertIn("Failure in voice connection", log.call_args.args[0])

    async def test_cog_loads_without_lavalink_or_secret(self):
        from cogs.menestrel.music import setup
        with patch.dict("os.environ", {}, clear=True):
            bot = Mock()
            setup(bot)
        bot.add_cog.assert_called_once()
        commands = {command.name for command in bot.add_cog.call_args.args[0].get_commands()}
        self.assertTrue({"play", "radio", "stop", "pause", "resume", "skip", "back", "queue", "now"}.issubset(commands))

    async def test_discord_radio_choices_match_web_catalogue(self):
        from cogs.menestrel.music import radio_autocomplete
        choices = await radio_autocomplete(SimpleNamespace(value=""))
        self.assertEqual([{"id": choice.value, "name": choice.name} for choice in choices], radio_choices())

    async def test_radio_rpc_only_accepts_catalogue_ids(self):
        real_manager = MusicManager()
        self.manager.search.side_effect = real_manager.search
        response = await self.post(action="play", source="radio", query="fip")
        self.assertEqual(response.status, 200)
        self.assertEqual(self.manager.play.call_args.args[1].title, "FIP")
        self.manager.play.reset_mock()
        response = await self.post(action="play", source="radio", query=RADIOS[0].url)
        self.assertEqual(response.status, 400)
        self.manager.play.assert_not_awaited()

    async def test_command_voice_errors_use_pycord_error_dispatch(self):
        from cogs.menestrel.music import Music
        cog = Music(Mock())
        ctx = SimpleNamespace(guild=SimpleNamespace(id=1), command=SimpleNamespace(name="play"),
                              author=SimpleNamespace(voice=None), respond=AsyncMock())
        with self.assertRaises(discord.ApplicationCommandInvokeError) as error:
            await cog.cog_before_invoke(ctx)
        await cog.cog_command_error(ctx, error.exception)
        ctx.respond.assert_awaited_once()
