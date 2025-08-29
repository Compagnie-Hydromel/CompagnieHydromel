import os
from dotenv import load_dotenv
from libs.log import Log
import sys
from libs.databases.bootstrap import init
import importlib
import subprocess

load_dotenv()

if len(sys.argv) < 2:
    Log.info("Starting all bots")

    barman_process = subprocess.Popen(
        ["python3", "bot.py", "barman"])
    menestrel_process = subprocess.Popen(
        ["python3", "bot.py", "menestrel"])
    archiveuse_process = subprocess.Popen(
        ["python3", "bot.py", "archiveuse"])
    webserver_process = subprocess.Popen(
        ["python3", "bot.py", "webserver"])

    barman_process.wait()
    menestrel_process.wait()
    archiveuse_process.wait()
    webserver_process.wait()
    exit()

init()

match sys.argv[1]:
    case 'webserver':
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        from contextlib import asynccontextmanager
        import importlib.util
        import uvicorn

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            Log.info(
                f"Webserver is starting on http://{os.getenv('HOST', '127.0.0.1')}:{os.getenv('WEB_PORT', 8000)}")
            yield
            Log.info("Webserver is shutting down...")

        app = FastAPI(debug=os.getenv("DEBUG", "false").lower()
                      == "true", lifespan=lifespan, docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json")

        def import_module_from_path(module_name: str, file_path: str):
            spec = importlib.util.spec_from_file_location(
                module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            return module

        controllers_path = os.path.join(
            os.path.dirname(__file__), "http", "controllers")
        for file in os.listdir(controllers_path):
            if file.endswith("_controller.py"):
                module_name = file[:-3]
                file_path = os.path.join(controllers_path, file)
                module = import_module_from_path(module_name, file_path)
                app.include_router(
                    module.router, prefix="/api")  # type: ignore

        middlewares_path = os.path.join(
            os.path.dirname(__file__), "http", "middlewares")
        for file in os.listdir(middlewares_path):
            if file.endswith("_middleware.py"):
                module_name = file[:-3]
                file_path = os.path.join(middlewares_path, file)
                module = import_module_from_path(module_name, file_path)
                app.middleware("http")(module.middleware)  # type: ignore

        app.mount("/", StaticFiles(directory="http/public",
                  html=True), name="public")

        uvicorn.run(app, port=os.getenv("WEB_PORT", 8000), host=os.getenv("WEB_HOST", "127.0.0.1"),
                    log_config=None, access_log=False)
    case 'barman' | 'menestrel' | 'archiveuse':
        import discord

        bot_name = sys.argv[1]

        intents: discord.Intents = discord.Intents.all()
        bot: discord.bot.Bot = discord.Bot(
            intents=intents, max_messages=1000000)

        # Load specific bot cogs
        for filename in os.listdir('./cogs/' + bot_name):
            if filename.endswith('.py'):
                bot.load_extension(f'cogs.{bot_name}.{filename[:-3]}')

        # Load common cogs
        for filename in os.listdir('./cogs/'):
            if filename.endswith('.py'):
                bot.load_extension(f'cogs.{filename[:-3]}')

        @bot.event
        async def on_ready():
            Log.info(bot_name.capitalize() + ' start with ' +
                     str(bot.user) + ' : ' + str(bot.user.id))

        bot_token_id: str = bot_name.upper() + "_TOKEN"
        if os.getenv(bot_token_id) is not None:
            bot.run(os.getenv(bot_token_id))
        else:
            Log.error(bot_token_id + " is not defined in .env file")
    case 'interactive':
        import code

        Log.info("Starting interactive mode")
        for filename in os.listdir('./libs/databases/models/'):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = f'libs.databases.models.{filename[:-3]}'
                globals()[filename[:-3]] = importlib.import_module(module_name)
                globals().update({name: getattr(globals()[filename[:-3]], name) for name in dir(
                    globals()[filename[:-3]]) if not name.startswith('_')})
        code.interact(local=globals())
    case 'migrate':
        from MIWOS.db import migrate

        migrate()
        Log.info("Migrations completed")
    case 'rollback':
        from MIWOS.db import rollback

        rollback(depth=int(sys.argv[2]) if len(sys.argv) > 2 else 1)
        Log.info("Rollback completed")
    case 'format':
        from libs.format import PythonFormatter

        formatter = PythonFormatter()
        exit_code = 0
        for file in formatter.format():
            exit_code = 1
            Log.warning(f"Formatted: {file}")
        exit(exit_code)
    case 'check-format':
        from libs.format import PythonFormatter

        formatter = PythonFormatter()
        exit_code = 0
        for file in formatter.check():
            exit_code = 1
            Log.warning(f"Needs formatting: {file}")
        exit(exit_code)
    case 'test':
        test_process = subprocess.run(
            ["python3", "-m", "unittest", "discover", "-s", "tests"]
        )
        exit(test_process.returncode)
    case _:
        Log.error("Subcommand not found")
        exit()
