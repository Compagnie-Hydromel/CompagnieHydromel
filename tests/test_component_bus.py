import asyncio
import json
import contextlib
import socket
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

import aiohttp

from libs.communication import BusError, ComponentBus
from libs.communication.protocol import MAX_MESSAGE_BYTES, decode, encode
from tests.bus_support import BusHarness, TOKENS


class TestComponentBus(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.harness = await BusHarness().start()
        self.web = self.harness.client("webserver")
        self.music = self.harness.client("menestrel")

    async def asyncTearDown(self):
        await self.harness.close()

    async def connect(self):
        await self.harness.connect(self.web, self.music)

    async def test_bidirectional_rpc_and_identity_comes_from_connection(self):
        async def identity(payload, context):
            return {"caller": context.caller, "value": payload["value"]}

        self.music.register("example.echo", identity, callers={"webserver"})
        self.web.register("example.echo", identity, callers={"menestrel"})
        await self.connect()
        result = await self.web.call("menestrel", "example.echo", {"value": 42, "caller": "barman"})
        self.assertEqual(result, {"caller": "webserver", "value": 42})
        self.assertEqual(await self.music.call("webserver", "example.echo", {"value": 7}), {"caller": "menestrel", "value": 7})

    async def test_every_component_can_expose_actions(self):
        barman, archiveuse = self.harness.client("barman"), self.harness.client("archiveuse")
        await self.harness.connect(self.web, self.music, barman, archiveuse)
        for caller, target in ((self.web, "menestrel"), (self.music, "barman"), (barman, "archiveuse"), (archiveuse, "webserver")):
            self.assertEqual((await caller.call(target, "system.ping"))["component"], target)

    async def test_caller_permissions_are_enforced_before_execution(self):
        handler = AsyncMock()
        self.music.register("private.action", handler, callers={"barman"})
        await self.connect()
        with self.assertRaises(BusError) as error:
            await self.web.call("menestrel", "private.action")
        self.assertEqual(error.exception.status, 403)
        handler.assert_not_awaited()

    async def test_offline_component_and_unknown_action(self):
        await self.connect()
        for target, action, status in (("barman", "system.ping", 503), ("menestrel", "not.exposed", 404)):
            with self.assertRaises(BusError) as error:
                await self.web.call(target, action)
            self.assertEqual(error.exception.status, status)

    async def test_handler_errors_preserve_status_and_generic_errors_hide_payloads(self):
        async def invalid(payload, context):
            raise BusError("Forbidden operation", code="forbidden", status=403)

        async def broken(payload, context):
            raise RuntimeError("secret not to expose")

        self.music.register("error.known", invalid, callers={"webserver"})
        self.music.register("error.unknown", broken, callers={"webserver"})
        await self.connect()
        with self.assertRaises(BusError) as error:
            await self.web.call("menestrel", "error.known")
        self.assertEqual(error.exception.status, 403)
        with patch("libs.communication.client.Log.warning") as log, self.assertRaises(BusError) as error:
            await self.web.call("menestrel", "error.unknown")
        self.assertEqual(error.exception.status, 500)
        self.assertNotIn("secret", str(error.exception))
        self.assertNotIn("secret", log.call_args.args[0])

    async def test_non_serializable_handler_result_is_reported(self):
        self.music.register("invalid.result", lambda payload, ctx: object(), callers={"webserver"})
        await self.connect()
        with self.assertRaises(BusError) as error:
            await self.web.call("menestrel", "invalid.result")
        self.assertEqual(error.exception.status, 502)

    async def test_timeout_cancels_provider_without_blocking_other_calls(self):
        entered, cancelled = asyncio.Event(), asyncio.Event()

        async def slow(payload, context):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        self.music.register("slow.action", slow, callers={"webserver"})
        await self.connect()
        call = asyncio.create_task(self.web.call("menestrel", "slow.action", timeout=0.1))
        await asyncio.wait_for(entered.wait(), 2)
        self.assertEqual((await self.web.call("menestrel", "system.ping"))["component"], "menestrel")
        with self.assertRaises(BusError) as error:
            await call
        self.assertEqual(error.exception.status, 504)
        await asyncio.wait_for(cancelled.wait(), 2)
        self.assertFalse(self.web._pending)
        self.assertFalse(self.harness.hub.pending)

    async def test_concurrent_calls_do_not_mix_responses(self):
        async def echo(payload, context):
            await asyncio.sleep((10 - payload) * 0.001)
            return payload

        self.music.register("echo", echo, callers={"webserver"})
        await self.connect()
        self.assertEqual(await asyncio.gather(*(self.web.call("menestrel", "echo", i) for i in range(10))), list(range(10)))

    async def test_events_only_reach_subscribers_and_keep_publisher_identity(self):
        got = asyncio.Future()
        self.web.on("menestrel.music.changed", lambda payload, context: got.set_result((payload, context.caller)))
        await self.connect()
        self.assertTrue(await self.music.publish("music.changed", {"guild_id": "123"}))
        self.assertEqual(await asyncio.wait_for(got, 2), ({"guild_id": "123"}, "menestrel"))

    async def test_registration_and_subscriptions_can_change_while_connected(self):
        await self.connect()
        self.music.register("new.action", lambda payload, context: 42, callers={"webserver"})
        # The provider registers before this ping is answered (same ordered WS).
        await self.music.call("webserver", "system.ping")
        self.assertEqual(await self.web.call("menestrel", "new.action"), 42)
        self.music.unregister("new.action")
        await self.music.call("webserver", "system.ping")
        with self.assertRaises(BusError):
            await self.web.call("menestrel", "new.action")

    async def test_disconnect_fails_pending_calls_and_does_not_replay_them(self):
        entered = asyncio.Event()
        calls = []

        async def slow(payload, context):
            calls.append(payload)
            entered.set()
            await asyncio.Event().wait()

        self.music.register("once", slow, callers={"webserver"})
        await self.connect()
        task = asyncio.create_task(self.web.call("menestrel", "once", 1))
        await asyncio.wait_for(entered.wait(), 2)
        await self.music.close()
        with self.assertRaises(BusError):
            await asyncio.wait_for(task, 2)
        replacement = self.harness.client("menestrel")
        replacement.register("once", slow, callers={"webserver"})
        await self.harness.connect(replacement)
        self.assertEqual((await self.web.call("menestrel", "system.ping"))["component"], "menestrel")
        self.assertEqual(calls, [1])

    async def test_reconnect_restores_registered_actions(self):
        await self.connect()
        # Closing the socket leaves the client reconnect loop alive.
        await self.music._socket.close()
        self.music._ready.clear()
        await self.music.wait_ready()
        self.assertEqual((await self.web.call("menestrel", "system.ping"))["component"], "menestrel")

    async def test_other_component_cannot_forge_a_pending_response(self):
        entered, release = asyncio.Event(), asyncio.Event()

        async def slow(payload, context):
            entered.set()
            await release.wait()
            return "real reply"

        self.music.register("slow", slow, callers={"webserver"})
        await self.connect()
        task = asyncio.create_task(self.web.call("menestrel", "slow"))
        await asyncio.wait_for(entered.wait(), 2)
        route_id = next(iter(self.harness.hub.pending))
        async with aiohttp.ClientSession() as client:
            async with client.ws_connect(self.harness.url, headers={"X-Component": "barman", "Authorization": "Bearer " + TOKENS["barman"]}) as socket:
                await socket.send_json({"type": "register"})
                await socket.receive_json()
                await socket.send_json({"type": "result", "id": route_id, "result": "forged"})
                await socket.send_json({"type": "call", "id": "barrier", "target": "webserver", "action": "system.ping"})
                self.assertEqual((await socket.receive_json())["id"], "barrier")
                self.assertFalse(task.done())
        release.set()
        self.assertEqual(await task, "real reply")

    async def test_caller_disconnect_cancels_remote_work_and_cleans_routes(self):
        entered, cancelled = asyncio.Event(), asyncio.Event()

        async def slow(payload, context):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        self.music.register("slow", slow, callers={"webserver"})
        await self.connect()
        task = asyncio.create_task(self.web.call("menestrel", "slow"))
        await asyncio.wait_for(entered.wait(), 2)
        await self.web.close()
        with self.assertRaises(BusError):
            await task
        await asyncio.wait_for(cancelled.wait(), 2)
        self.assertFalse(self.harness.hub.pending)

    async def test_missing_or_wrong_token_is_denied(self):
        async with aiohttp.ClientSession() as client:
            for headers in ({}, {"X-Component": "webserver", "Authorization": "Bearer wrong"}, {"X-Component": "unknown", "Authorization": "Bearer web-secret"}):
                with self.assertRaises(aiohttp.WSServerHandshakeError) as error:
                    await client.ws_connect(self.harness.url, headers=headers)
                self.assertEqual(error.exception.status, 403)

    async def test_duplicate_component_does_not_replace_existing_peer(self):
        await self.connect()
        async with aiohttp.ClientSession() as client:
            with self.assertRaises(aiohttp.WSServerHandshakeError):
                await client.ws_connect(self.harness.url, headers={"X-Component": "webserver", "Authorization": "Bearer " + TOKENS["webserver"]})
        self.assertTrue(self.web.connected)

    async def test_unregistered_connections_and_malformed_messages_are_closed(self):
        async with aiohttp.ClientSession() as client:
            async with client.ws_connect(self.harness.url, headers={"X-Component": "barman", "Authorization": "Bearer " + TOKENS["barman"]}) as socket:
                await socket.send_json({"type": "call", "id": "early", "target": "webserver", "action": "system.ping"})
                self.assertEqual((await socket.receive()).type, aiohttp.WSMsgType.CLOSE)

    async def test_events_cannot_impersonate_another_component(self):
        async with aiohttp.ClientSession() as client:
            async with client.ws_connect(self.harness.url, headers={"X-Component": "barman", "Authorization": "Bearer " + TOKENS["barman"]}) as socket:
                await socket.send_json({"type": "register"})
                await socket.receive_json()
                await socket.send_json({"type": "publish", "topic": "menestrel.music.changed"})
                self.assertEqual((await socket.receive()).type, aiohttp.WSMsgType.CLOSE)

    async def test_unconfigured_client_is_optional_and_offline_events_are_not_queued(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(ComponentBus.from_env("menestrel"))
        self.assertFalse(await self.music.publish("music.changed"))
        with self.assertRaises(BusError):
            await self.music.call("webserver", "system.ping")

    def test_protocol_bounds_and_non_json_values(self):
        for text in ("[]", "invalid", json.dumps({"value": "x" * MAX_MESSAGE_BYTES})):
            with self.assertRaises(ValueError):
                decode(text)
        for data in ({"value": "x" * MAX_MESSAGE_BYTES}, {"value": float("nan")}):
            with self.assertRaises(ValueError):
                encode(data)


class TestFastAPIComponentBus(unittest.IsolatedAsyncioTestCase):
    async def test_production_websocket_route_with_real_asgi_server(self):
        import uvicorn
        from fastapi import FastAPI
        from libs.communication.hub import ComponentHub
        from libs.utils.utils import Utils

        controller = Utils.import_module_from_path("integration_component_bus_controller", "http/controllers/component_bus_controller.py")
        app = FastAPI()
        hub = ComponentHub(TOKENS)
        app.state.component_hub = hub
        app.include_router(controller.router, prefix="/api")
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_config=None, log_level="critical", lifespan="off", ws_max_size=MAX_MESSAGE_BYTES))
        server.capture_signals = contextlib.nullcontext
        task = asyncio.create_task(server.serve(sockets=[listener]))
        url = f"ws://127.0.0.1:{port}/api/internal/bus"
        client = ComponentBus("webserver", url, TOKENS["webserver"], reconnect_delay=0.01)
        try:
            await client.start()
            await client.wait_ready()
            self.assertEqual((await client.call("webserver", "system.ping"))["component"], "webserver")
            async with aiohttp.ClientSession() as browser:
                with self.assertRaises(aiohttp.WSServerHandshakeError) as error:
                    await browser.ws_connect(url, headers={"Cookie": "session=not-a-bus-token"})
                self.assertEqual(error.exception.status, 403)
        finally:
            await client.close()
            await hub.close()
            server.should_exit = True
            await asyncio.wait_for(task, 5)
            listener.close()
