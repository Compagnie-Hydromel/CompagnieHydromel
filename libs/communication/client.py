import asyncio
import inspect
import math
import os
from uuid import uuid4

import aiohttp

from libs.communication.protocol import (
    BusError, CallContext, DEFAULT_COMPONENTS, MAX_MESSAGE_BYTES, MAX_PENDING,
    MAX_TIMEOUT, component_names, decode, encode, token_key, valid_name,
)
from libs.log import Log


class ComponentBus:
    """Async RPC and best-effort events. Calls are never replayed on reconnect."""

    def __init__(self, component, url, token, *, reconnect_delay=1):
        if not valid_name(component):
            raise ValueError("Invalid component name")
        self.component, self.url, self.token = component, url, token
        self.reconnect_delay = reconnect_delay
        self._handlers = {}
        self._subscriptions = {}
        self._pending = {}
        self._invocations = {}
        self._tasks = set()
        self._ready = asyncio.Event()
        self._closed = asyncio.Event()
        self._writer = asyncio.Lock()
        self._socket = None
        self._runner = None
        self.register("system.ping", self._ping, callers=set(DEFAULT_COMPONENTS) | component_names())

    @classmethod
    def from_env(cls, component):
        token = os.getenv(token_key(component))
        if not token:
            return None
        return cls(component, os.getenv("BUS_URL", "ws://127.0.0.1:8000/api/internal/bus"), token)

    async def _ping(self, payload, context):
        return {"component": self.component, "protocol": 1}

    @property
    def connected(self):
        return self._ready.is_set()

    def register(self, action, handler, *, callers):
        if isinstance(callers, str):
            raise ValueError("Callers must be an explicit collection of component names")
        callers = set(callers)
        if not valid_name(action) or not callable(handler) or any(not valid_name(name) for name in callers):
            raise ValueError("Invalid action registration")
        if (action not in self._handlers and len(self._handlers) >= 128) or len(callers) > 128:
            raise ValueError("Too many registered actions/callers")
        self._handlers[action] = (handler, callers)
        self._refresh()

    def unregister(self, action):
        self._handlers.pop(action, None)
        self._refresh()

    def on(self, topic, handler):
        if not valid_name(topic) or not callable(handler):
            raise ValueError("Invalid event subscription")
        if topic not in self._subscriptions and len(self._subscriptions) >= 128:
            raise ValueError("Too many event subscriptions")
        self._subscriptions.setdefault(topic, []).append(handler)
        self._refresh()

    def off(self, topic, handler):
        handlers = self._subscriptions.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)
        if not handlers:
            self._subscriptions.pop(topic, None)
        self._refresh()

    def _spawn(self, coroutine):
        task = asyncio.create_task(coroutine)
        self._tasks.add(task)

        def finished(done):
            self._tasks.discard(done)
            if not done.cancelled() and done.exception() is not None:
                Log.warning(f"Bus background task failed [{self.component}]: {type(done.exception()).__name__}")

        task.add_done_callback(finished)
        return task

    def _refresh(self):
        if self.connected:
            self._spawn(self._refresh_connected())

    async def _refresh_connected(self):
        try:
            await self._send_registration()
        except BusError:
            pass

    async def start(self):
        if self._runner is None:
            self._runner = asyncio.create_task(self._run())

    async def wait_ready(self, timeout=5):
        try:
            await asyncio.wait_for(self._ready.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise BusError("Bus inter-composants indisponible.") from None

    async def _send(self, message, *, socket=None):
        text = encode(message)
        socket = socket if socket is not None else self._socket

        async def write():
            async with self._writer:
                if socket is None or socket is not self._socket or socket.closed:
                    raise BusError("Bus inter-composants déconnecté.")
                await socket.send_str(text)

        try:
            await asyncio.wait_for(write(), timeout=5)
        except (aiohttp.ClientError, ConnectionError, RuntimeError, asyncio.TimeoutError):
            raise BusError("Bus inter-composants déconnecté.") from None

    async def _send_registration(self):
        await self._send({"type": "register", "actions": {name: sorted(callers) for name, (_, callers) in self._handlers.items()},
                          "subscriptions": list(self._subscriptions)})

    async def call(self, target, action, payload=None, *, timeout=30):
        if not valid_name(target) or not valid_name(action):
            raise ValueError("Invalid RPC target/action")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= MAX_TIMEOUT:
            raise ValueError("Invalid RPC timeout")
        if not self.connected:
            raise BusError("Bus inter-composants indisponible.")
        if len(self._pending) >= MAX_PENDING:
            raise BusError("Trop d'appels en cours.", code="busy", status=429)
        request_id = uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        socket = self._socket
        sent = False
        deadline = asyncio.get_running_loop().time() + timeout
        try:
            await asyncio.wait_for(self._send({"type": "call", "id": request_id, "target": target, "action": action,
                                              "payload": payload, "timeout": timeout}, socket=socket), timeout=timeout)
            sent = True
            return await asyncio.wait_for(future, timeout=max(0, deadline - asyncio.get_running_loop().time()))
        except asyncio.TimeoutError:
            raise BusError("Délai d'appel dépassé.", code="timeout", status=504) from None
        finally:
            self._pending.pop(request_id, None)
            if sent and future.cancelled():
                try:
                    await self._send({"type": "cancel", "id": request_id}, socket=socket)
                except BusError:
                    pass
            if not future.done():
                future.cancel()
            elif not future.cancelled():
                future.exception()  # Also consume disconnect errors if sending failed.

    async def publish(self, topic, payload=None):
        if not valid_name(topic) or not valid_name(self.component + "." + topic):
            raise ValueError("Invalid event name")
        if not self.connected:
            return False
        try:
            await self._send({"type": "publish", "topic": self.component + "." + topic, "payload": payload})
            return True
        except BusError:
            return False

    async def _invoke(self, message, socket):
        route_id = message["id"]
        try:
            entry = self._handlers.get(message.get("action"))
            if entry is None:
                raise BusError("Action inconnue.", code="not_found", status=404)
            handler, callers = entry
            if message.get("caller") not in callers:
                raise BusError("Appel refusé.", code="forbidden", status=403)
            result = handler(message.get("payload"), CallContext(message["caller"]))
            if inspect.isawaitable(result):
                result = await result
            response = {"type": "result", "id": route_id, "result": result}
            try:
                encode(response)
            except (ValueError, TypeError):
                raise BusError("Réponse non sérialisable ou trop volumineuse.", code="invalid_result", status=502) from None
        except BusError as error:
            response = {"type": "error", "id": route_id, "error": error.data()}
        except asyncio.CancelledError:
            raise
        except Exception as error:
            Log.warning(f"Bus action failed [{self.component}/{message.get('action')}]: {type(error).__name__}")
            response = {"type": "error", "id": route_id,
                        "error": BusError("Erreur du composant distant.", code="internal", status=500).data()}
        finally:
            self._invocations.pop(route_id, None)
        try:
            await self._send(response, socket=socket)
        except BusError:
            pass

    async def _event(self, handler, message):
        try:
            result = handler(message.get("payload"), CallContext(message["publisher"]))
            if inspect.isawaitable(result):
                await result
        except Exception as error:
            Log.warning(f"Bus event handler failed [{self.component}]: {type(error).__name__}")

    async def _receive(self, message, socket):
        kind = message.get("type")
        if kind == "ready":
            self._ready.set()
        elif kind in ("result", "error"):
            future = self._pending.get(message.get("id"))
            if future and not future.done():
                if kind == "error":
                    future.set_exception(BusError.from_data(message["error"]))
                else:
                    future.set_result(message.get("result"))
        elif kind == "invoke":
            if len(self._invocations) >= MAX_PENDING:
                await self._send({"type": "error", "id": message["id"],
                                  "error": BusError("Composant occupé.", code="busy", status=429).data()}, socket=socket)
            else:
                self._invocations[message["id"]] = self._spawn(self._invoke(message, socket))
        elif kind == "cancel":
            task = self._invocations.get(message.get("id"))
            if task:
                task.cancel()
        elif kind == "event":
            # Bound work from noisy publishers; events are deliberately best-effort.
            for handler in self._subscriptions.get(message.get("topic"), []):
                if len(self._tasks) < 128:
                    self._spawn(self._event(handler, message))
        else:
            raise ValueError("Invalid bus response")

    async def _disconnected(self):
        self._ready.clear()
        self._socket = None
        for future in self._pending.values():
            if not future.done():
                future.set_exception(BusError("Bus inter-composants déconnecté."))
        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._invocations.clear()

    async def _run(self):
        delay = self.reconnect_delay
        while not self._closed.is_set():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self.url, headers={"X-Component": self.component, "Authorization": "Bearer " + self.token},
                                                  heartbeat=20, max_msg_size=MAX_MESSAGE_BYTES, timeout=aiohttp.ClientWSTimeout(ws_close=5)) as socket:
                        self._socket = socket
                        await self._send_registration()
                        delay = self.reconnect_delay
                        async for message in socket:
                            if message.type != aiohttp.WSMsgType.TEXT:
                                break
                            await self._receive(decode(message.data), socket)
            except asyncio.CancelledError:
                raise
            except (aiohttp.ClientError, ConnectionError, RuntimeError, asyncio.TimeoutError, BusError, ValueError, TypeError, KeyError):
                # Never log connection headers or URLs that might contain secrets.
                pass
            finally:
                await self._disconnected()
            try:
                await asyncio.wait_for(self._closed.wait(), timeout=delay)
            except asyncio.TimeoutError:
                delay = min(delay * 2, 10)

    async def close(self):
        self._closed.set()
        if self._socket:
            await self._socket.close()
        if self._runner:
            self._runner.cancel()
            await asyncio.gather(self._runner, return_exceptions=True)
            self._runner = None
        await self._disconnected()
