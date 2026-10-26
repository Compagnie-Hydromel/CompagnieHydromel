import asyncio
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from libs.databases.models.application_model import ApplicationModel
from libs.utils.utils import Utils
from libs.log import Log
import discord
from libs.communication import ComponentBus
from libs.communication.hub import ComponentHub
from libs.communication.protocol import MAX_MESSAGE_BYTES, configured_tokens


@asynccontextmanager
async def lifespan(app: FastAPI):
    Log.info(
        f"Webserver is starting on http://{os.getenv('HOST', '127.0.0.1')}:{os.getenv('WEB_PORT', 8000)}")
    # Initialize Discord bot with commands disabled
    discord_bot = discord.Bot(
        intents=discord.Intents.all(), auto_sync_commands=False)

    @discord_bot.event
    async def on_ready():
        ApplicationModel.set_bot(discord_bot)
        Log.info(
            f"Discord bot for webserver is ready. Logged in as {discord_bot.user}")

    token_used = (os.getenv("WEBSERVER_BOT") or "BARMAN").upper() + "_TOKEN"

    token_value = os.getenv(token_used)
    if not token_value:
        raise RuntimeError(f"Discord bot token '{token_used}' is not set or invalid.")

    app.state.component_hub = ComponentHub(configured_tokens())
    app.state.component_bus = ComponentBus.from_env("webserver")
    task = asyncio.create_task(discord_bot.start(token_value))
    try:
        if app.state.component_bus:
            await app.state.component_bus.start()
        yield
    finally:
        if app.state.component_bus:
            await app.state.component_bus.close()
        await app.state.component_hub.close()
        await discord_bot.close()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        Log.info("Webserver is shutting down...")

app = FastAPI(lifespan=lifespan, docs_url="/api/docs",
              redoc_url="/api/redoc", openapi_url="/api/openapi.json")


def load_modules_from_directory(directory: str, callback: callable):
    path = os.path.join(os.path.dirname(__file__), directory)
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            file_path = os.path.join(path, file)
            module = Utils.import_module_from_path(module_name, file_path)
            callback(module)


load_modules_from_directory(
    "controllers", lambda module: app.include_router(module.router, prefix="/api"))

load_modules_from_directory(
    "middlewares", lambda module: app.middleware("http")(module.middleware))
app.add_middleware(SessionMiddleware, secret_key=os.getenv(
    "SESSION_SECRET_KEY", "supersecretkey"), session_cookie="session")

app.mount("/", StaticFiles(directory="http/public",
                           html=True), name="public")

uvicorn.run(app, port=int(os.getenv("WEB_PORT", 8000)), host=os.getenv("WEB_HOST", "127.0.0.1"),
            log_config=None, access_log=False, ws_max_size=MAX_MESSAGE_BYTES)
