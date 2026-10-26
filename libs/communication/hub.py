import asyncio
import hmac
import math
from dataclasses import dataclass, field
from uuid import uuid4

from starlette.websockets import WebSocketDisconnect

from libs.communication.protocol import BusError, MAX_PENDING, MAX_TIMEOUT, decode, encode, valid_name


TRANSPORT_ERRORS = (ConnectionError, RuntimeError,
                    asyncio.TimeoutError, WebSocketDisconnect)


@dataclass(eq=False)
class Peer:
    name: str
    socket: object
    actions: dict = field(default_factory=dict)
    subscriptions: set = field(default_factory=set)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def send(self, message):
        text = encode(message)

        async def write():
            async with self.lock:
                await self.socket.send_text(text)

        await asyncio.wait_for(write(), timeout=5)


@dataclass
class Pending:
    caller: Peer
    caller_id: str
    target: Peer
    timer: object = None


class ComponentHub:
    """One authenticated connection per component; explicitly registered actions only."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.peers = {}
        self.pending = {}
        self.closed = False

    async def serve(self, socket):
        name = socket.headers.get("x-component", "")
        expected = self.tokens.get(name)
        provided = socket.headers.get("authorization", "")
        if self.closed or not expected or not hmac.compare_digest(provided.encode(), ("Bearer " + expected).encode()):
            await socket.close(code=1008)
            return
        if name in self.peers:
            await socket.close(code=1008)
            return
        peer = Peer(name, socket)
        # Reserve identity before accept (two simultaneous connections cannot win).
        self.peers[name] = peer
        try:
            await socket.accept()
            initial = decode(await asyncio.wait_for(socket.receive_text(), timeout=10))
            if initial.get("type") != "register":
                raise ValueError("Registration required")
            await self._register(peer, initial)
            while not self.closed:
                message = decode(await socket.receive_text())
                kind = message.get("type")
                if kind == "register":
                    await self._register(peer, message)
                elif kind == "call":
                    await self._call(peer, message)
                elif kind in ("result", "error"):
                    await self._reply(peer, message)
                elif kind == "cancel":
                    for route_id, pending in list(self.pending.items()):
                        if pending.caller is peer and pending.caller_id == message.get("id"):
                            await self._cancel(route_id)
                elif kind == "publish":
                    await self._publish(peer, message)
                else:
                    raise ValueError("Unknown bus message")
        except (WebSocketDisconnect, ConnectionError, asyncio.TimeoutError):
            pass
        except (ValueError, TypeError, KeyError):
            await socket.close(code=1008)
        finally:
            await self._remove(peer)
            try:
                await socket.close(code=1000)
            except TRANSPORT_ERRORS:
                pass

    async def _register(self, peer, message):
        actions, subscriptions = message.get(
            "actions", {}), message.get("subscriptions", [])
        if not isinstance(actions, dict) or len(actions) > 128 or not isinstance(subscriptions, list) or len(subscriptions) > 128:
            raise ValueError("Invalid registration")
        if any(not valid_name(action) or not isinstance(callers, list) or len(callers) > 128
               or any(not valid_name(caller) for caller in callers) for action, callers in actions.items()):
            raise ValueError("Invalid action permissions")
        if any(not valid_name(topic) for topic in subscriptions):
            raise ValueError("Invalid subscriptions")
        peer.actions = {action: set(callers)
                        for action, callers in actions.items()}
        peer.subscriptions = set(subscriptions)
        await peer.send({"type": "ready"})

    async def _call(self, peer, message):
        request_id = message.get("id")
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 64:
            raise ValueError("Invalid request ID")
        if any(item.caller is peer and item.caller_id == request_id for item in self.pending.values()):
            raise ValueError("Duplicate request ID")
        target = self.peers.get(message.get("target"))
        action = message.get("action")
        error = None
        if not target:
            error = BusError("Composant indisponible.")
        elif not valid_name(action) or action not in target.actions:
            error = BusError("Action inconnue.", code="not_found", status=404)
        elif peer.name not in target.actions[action]:
            error = BusError("Appel inter-composants refusé.",
                             code="forbidden", status=403)
        elif len(self.pending) >= 1024 or sum(item.caller is peer for item in self.pending.values()) >= MAX_PENDING:
            error = BusError("Trop d'appels en cours.",
                             code="busy", status=429)
        timeout = message.get("timeout", 30)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= MAX_TIMEOUT:
            raise ValueError("Invalid timeout")
        if error:
            await peer.send({"type": "error", "id": request_id, "error": error.data()})
            return
        route_id = uuid4().hex
        pending = Pending(peer, request_id, target)
        self.pending[route_id] = pending
        pending.timer = asyncio.create_task(self._expire(route_id, timeout))
        try:
            await target.send({"type": "invoke", "id": route_id, "action": action,
                               "payload": message.get("payload"), "caller": peer.name})
        except (*TRANSPORT_ERRORS, ValueError):
            await self._finish(route_id, error=BusError("Composant indisponible.").data())

    async def _reply(self, peer, message):
        route_id = message.get("id")
        pending = self.pending.get(route_id)
        if pending is None or pending.target is not peer:
            # Late reply, or an attempt to answer for another component.
            return
        if message["type"] == "error":
            error = message.get("error")
            if (not isinstance(error, dict) or not isinstance(error.get("message"), str)
                    or not isinstance(error.get("code"), str) or not isinstance(error.get("status"), int)
                    or not 400 <= error["status"] <= 599):
                raise ValueError("Invalid RPC error")
            await self._finish(route_id, error=error)
        else:
            await self._finish(route_id, result=message.get("result"))

    async def _finish(self, route_id, *, result=None, error=None):
        pending = self.pending.pop(route_id, None)
        if pending is None:
            return
        if pending.timer is not asyncio.current_task():
            pending.timer.cancel()
        message = {"type": "error" if error else "result",
                   "id": pending.caller_id}
        message["error" if error else "result"] = error if error else result
        try:
            await pending.caller.send(message)
        except (*TRANSPORT_ERRORS, ValueError):
            pass

    async def _cancel(self, route_id):
        pending = self.pending.pop(route_id, None)
        if pending:
            if pending.timer is not asyncio.current_task():
                pending.timer.cancel()
            try:
                await pending.target.send({"type": "cancel", "id": route_id})
            except TRANSPORT_ERRORS:
                pass

    async def _expire(self, route_id, timeout):
        await asyncio.sleep(timeout)
        pending = self.pending.get(route_id)
        if pending:
            await self._finish(route_id, error=BusError("Délai d'appel dépassé.", code="timeout", status=504).data())
            try:
                await pending.target.send({"type": "cancel", "id": route_id})
            except TRANSPORT_ERRORS:
                pass

    async def _publish(self, peer, message):
        topic = message.get("topic")
        if not valid_name(topic) or not topic.startswith(peer.name + "."):
            raise ValueError("Events must belong to their publisher")
        event = {"type": "event", "topic": topic,
                 "payload": message.get("payload"), "publisher": peer.name}
        recipients = [recipient for recipient in self.peers.values(
        ) if topic in recipient.subscriptions]
        await asyncio.gather(*(recipient.send(event) for recipient in recipients), return_exceptions=True)

    async def _remove(self, peer):
        if self.peers.get(peer.name) is peer:
            del self.peers[peer.name]
        for route_id, pending in list(self.pending.items()):
            if pending.caller is peer:
                await self._cancel(route_id)
            elif pending.target is peer:
                await self._finish(route_id, error=BusError("Composant déconnecté.").data())

    async def close(self):
        self.closed = True
        peers = list(self.peers.values())
        await asyncio.gather(*(peer.socket.close(code=1001) for peer in peers), return_exceptions=True)
        for peer in peers:
            await self._remove(peer)
