from aiohttp import WSMsgType, web
from aiohttp.test_utils import TestServer
from starlette.websockets import WebSocketDisconnect

from libs.communication import ComponentBus
from libs.communication.hub import ComponentHub


TOKENS = {"webserver": "web-secret", "menestrel": "music-secret", "barman": "bar-secret", "archiveuse": "archive-secret"}


class SocketAdapter:
    """Run the production hub against real WebSockets without starting Discord."""

    def __init__(self, request):
        self.request = request
        self.headers = request.headers
        self.socket = web.WebSocketResponse()

    async def accept(self):
        await self.socket.prepare(self.request)

    async def send_text(self, text):
        await self.socket.send_str(text)

    async def receive_text(self):
        message = await self.socket.receive()
        if message.type != WSMsgType.TEXT:
            raise WebSocketDisconnect()
        return message.data

    async def close(self, code=1000):
        if self.socket.prepared:
            await self.socket.close(code=code)


class BusHarness:
    def __init__(self):
        self.hub = ComponentHub(TOKENS)
        self.clients = []

    async def start(self):
        app = web.Application()

        async def endpoint(request):
            socket = SocketAdapter(request)
            await self.hub.serve(socket)
            return socket.socket if socket.socket.prepared else web.Response(status=403)

        app.router.add_get("/api/internal/bus", endpoint)
        self.server = TestServer(app)
        await self.server.start_server()
        self.url = str(self.server.make_url("/api/internal/bus").with_scheme("ws"))
        return self

    def client(self, name):
        client = ComponentBus(name, self.url, TOKENS[name], reconnect_delay=0.01)
        self.clients.append(client)
        return client

    async def connect(self, *clients):
        for client in clients:
            await client.start()
        for client in clients:
            await client.wait_ready()

    async def close(self):
        for client in self.clients:
            await client.close()
        await self.hub.close()
        await self.server.close()
