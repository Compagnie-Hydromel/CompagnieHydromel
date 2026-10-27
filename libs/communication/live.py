import asyncio
from collections import defaultdict

from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect


class LiveUpdates:
    """Coalesced change notifications; no background database polling."""

    def __init__(self):
        self.listeners = defaultdict(set)

    def changed(self, guild_id, topic):
        for event in self.listeners.get((str(guild_id), topic), ()):
            event.set()

    def invalidate_all(self):
        for listeners in self.listeners.values():
            for event in listeners:
                event.set()

    def invalidate_topic(self, topic):
        for (_, name), listeners in self.listeners.items():
            if name == topic:
                for event in listeners:
                    event.set()

    async def stream(self, socket, guild_id, topic, snapshot):
        # Reject cross-site WebSocket connections using the session cookie.
        from urllib.parse import urlsplit
        origin = urlsplit(socket.headers.get("origin", ""))
        if origin.netloc != socket.headers.get("host") or origin.scheme not in ("http", "https"):
            await socket.close(code=1008)
            return
        event = asyncio.Event()
        key = (str(guild_id), topic)
        self.listeners[key].add(event)
        receiver = None
        try:
            await socket.accept()
            receiver = asyncio.create_task(socket.receive_text())
            data = await snapshot()
            while True:
                await asyncio.wait_for(socket.send_json({"type": "snapshot", "data": data}), 10)
                waiter = asyncio.create_task(event.wait())
                try:
                    done, _ = await asyncio.wait((receiver, waiter), return_when=asyncio.FIRST_COMPLETED)
                    if receiver in done:
                        # This is a server-only stream; clients cannot invoke actions.
                        receiver.result()
                        await socket.close(code=1008)
                        return
                finally:
                    waiter.cancel()
                    await asyncio.gather(waiter, return_exceptions=True)
                event.clear()
                await asyncio.sleep(0.1)
                data = await snapshot()
        except HTTPException as error:
            await socket.close(code=4000 + error.status_code if error.status_code in (401, 403, 404) else 1013)
        except (WebSocketDisconnect, ConnectionError, RuntimeError, asyncio.TimeoutError):
            pass
        finally:
            self.listeners[key].discard(event)
            if not self.listeners[key]:
                del self.listeners[key]
            if receiver:
                receiver.cancel()
                await asyncio.gather(receiver, return_exceptions=True)


live_updates = LiveUpdates()
_tasks = set()


def notify_change(guild_id, topic):
    """Notify locally and relay committed changes from bots to the webserver."""
    from libs.databases.models.application_model import ApplicationModel
    live_updates.changed(guild_id, topic)
    bot = getattr(ApplicationModel, "bot", None)
    bus = getattr(bot, "component_bus", None)
    if bus:
        task = asyncio.create_task(bus.publish(
            "live.changed", {"guild_id": str(guild_id), "topic": topic}))
        _tasks.add(task)
        task.add_done_callback(_tasks.discard)


def receive_change(payload, context):
    if isinstance(payload, dict) and payload.get("topic") in ("dashboard", "music"):
        live_updates.changed(payload.get("guild_id"), payload["topic"])


def register_discord_changes(bot):
    async def ready():
        live_updates.invalidate_all()

    async def user_changed(before, after):
        for guild in bot.guilds:
            if guild.get_member(after.id):
                live_updates.changed(guild.id, "dashboard")

    bot.add_listener(ready, "on_ready")
    bot.add_listener(user_changed, "on_user_update")

    async def changed(*args):
        item = args[-1]
        guild = getattr(item, "guild", None)
        if guild is None and args:
            guild = getattr(args[0], "guild", None)
        if guild is None:
            guild = item
        live_updates.changed(guild.id, "dashboard")
        live_updates.changed(guild.id, "music")

    for name in ("on_voice_state_update", "on_member_update", "on_member_join", "on_member_remove",
                 "on_guild_channel_create", "on_guild_channel_update", "on_guild_channel_delete",
                 "on_guild_role_create", "on_guild_role_update", "on_guild_role_delete",
                 "on_guild_update", "on_guild_remove"):
        bot.add_listener(changed, name)
