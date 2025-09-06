import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from libs.utils.utils import Utils
from libs.log import Log


@asynccontextmanager
async def lifespan(app: FastAPI):
    Log.info(
        f"Webserver is starting on http://{os.getenv('HOST', '127.0.0.1')}:{os.getenv('WEB_PORT', 8000)}")
    yield
    Log.info("Webserver is shutting down...")

app = FastAPI(debug=os.getenv("DEBUG", "false").lower()
              == "true", lifespan=lifespan, docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json")


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

app.mount("/", StaticFiles(directory="http/public",
                           html=True), name="public")

uvicorn.run(app, port=os.getenv("WEB_PORT", 8000), host=os.getenv("WEB_HOST", "127.0.0.1"),
            log_config=None, access_log=False)
