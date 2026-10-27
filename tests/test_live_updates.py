import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect

from libs.communication.live import LiveUpdates, notify_change, receive_change, live_updates
from libs.databases.models.application_model import ApplicationModel
from libs.databases.models.guild_user import GuildUser
from libs.music.music_manager import MusicManager


class Socket:
    def __init__(self, origin="https://example.com"):
        self.headers = {"host": "example.com", "origin": origin}
        self.messages = asyncio.Queue()
        self.incoming = asyncio.Queue()
        self.accept = AsyncMock()
        self.close = AsyncMock()

    async def send_json(self, message):
        await self.messages.put(message)

    async def receive_text(self):
        value = await self.incoming.get()
        if value is None:
            raise WebSocketDisconnect()
        return value


class TestLiveUpdates(unittest.IsolatedAsyncioTestCase):
    async def start_stream(self, snapshot):
        hub, socket = LiveUpdates(), Socket()
        task = asyncio.create_task(hub.stream(socket, "123", "dashboard", snapshot))
        self.addAsyncCleanup(self.stop_stream, task)
        return hub, socket, task

    async def stop_stream(self, task):
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def message(self, socket):
        return await asyncio.wait_for(socket.messages.get(), 1)

    async def test_initial_snapshot_then_only_updates_after_changes(self):
        snapshot = AsyncMock(side_effect=[{"xp": 1}, {"xp": 2}])
        hub, socket, task = await self.start_stream(snapshot)
        self.assertEqual(await self.message(socket), {"type": "snapshot", "data": {"xp": 1}})
        await asyncio.sleep(0.15)
        self.assertEqual(snapshot.await_count, 1)
        hub.changed("123", "dashboard")
        self.assertEqual((await self.message(socket))["data"], {"xp": 2})
        await socket.incoming.put(None)
        await task
        self.assertFalse(hub.listeners)

    async def test_events_are_scoped_and_bursts_are_coalesced(self):
        snapshot = AsyncMock(return_value={})
        hub, socket, _ = await self.start_stream(snapshot)
        await self.message(socket)
        hub.changed("456", "dashboard")
        hub.changed("123", "music")
        await asyncio.sleep(0.15)
        self.assertEqual(snapshot.await_count, 1)
        for _ in range(20):
            hub.changed("123", "dashboard")
        await self.message(socket)
        self.assertEqual(snapshot.await_count, 2)

    async def test_authorization_is_rechecked_before_sending_updates(self):
        snapshot = AsyncMock(side_effect=[{}, HTTPException(403, "Denied")])
        hub, socket, task = await self.start_stream(snapshot)
        await self.message(socket)
        hub.changed("123", "dashboard")
        await asyncio.wait_for(task, 1)
        socket.close.assert_awaited_once_with(code=4403)
        self.assertTrue(socket.messages.empty())
        self.assertFalse(hub.listeners)

    async def test_unauthenticated_connection_gets_no_data(self):
        _, socket, task = await self.start_stream(AsyncMock(side_effect=HTTPException(401)))
        await task
        socket.close.assert_awaited_once_with(code=4401)
        self.assertTrue(socket.messages.empty())

    async def test_cross_origin_connection_is_rejected(self):
        socket, snapshot = Socket("https://evil.example"), AsyncMock()
        await LiveUpdates().stream(socket, "123", "dashboard", snapshot)
        socket.close.assert_awaited_once_with(code=1008)
        socket.accept.assert_not_awaited()
        snapshot.assert_not_awaited()

    async def test_reconnect_resynchronization(self):
        snapshot = AsyncMock(return_value={})
        hub, socket, _ = await self.start_stream(snapshot)
        await self.message(socket)
        hub.invalidate_all()
        await self.message(socket)
        self.assertEqual(snapshot.await_count, 2)

    async def test_catalogue_changes_only_refresh_music(self):
        hub = LiveUpdates()
        dashboard, music = asyncio.Event(), asyncio.Event()
        hub.listeners[("123", "dashboard")].add(dashboard)
        hub.listeners[("123", "music")].add(music)
        hub.invalidate_topic("music")
        self.assertTrue(music.is_set())
        self.assertFalse(dashboard.is_set())

    async def test_bus_reconnect_invalidates_snapshots(self):
        from libs.communication.client import ComponentBus
        bus = ComponentBus("webserver", "ws://example.com", "secret")
        bus.on_ready = Mock()
        await bus._receive({"type": "ready"}, None)
        bus.on_ready.assert_called_once()

    async def test_bot_changes_are_relayed_over_the_component_bus(self):
        bus = SimpleNamespace(publish=AsyncMock())
        with patch.object(ApplicationModel, "bot", SimpleNamespace(component_bus=bus), create=True):
            notify_change(123, "dashboard")
            await asyncio.sleep(0)
        bus.publish.assert_awaited_once_with("live.changed", {"guild_id": "123", "topic": "dashboard"})

    async def test_received_bus_event_notifies_local_clients(self):
        with patch.object(live_updates, "changed") as changed:
            receive_change({"guild_id": "123", "topic": "music"}, None)
            changed.assert_called_once_with("123", "music")

    async def test_saved_profile_notifies_after_commit(self):
        member = object.__new__(GuildUser)
        member._attributes = {"guild": SimpleNamespace(discord_id="123")}
        member._modified_attributes = {}
        with patch("libs.communication.live.notify_change") as changed:
            member.afterSave()
            changed.assert_called_once_with("123", "dashboard")

    async def test_music_controls_and_natural_track_end_notify(self):
        manager = MusicManager()
        manager.on_change = Mock()
        manager.voice_clients = Mock()
        await manager.pause()
        manager.on_change.assert_called_once()
        manager.on_change.reset_mock()
        manager._advance = AsyncMock()
        await manager._finished(manager._generation, None)
        manager.on_change.assert_called_once()
