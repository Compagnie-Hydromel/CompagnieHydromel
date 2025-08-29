from urllib.request import Request
from fastapi.responses import FileResponse


async def spa_redirect_middleware(request: Request, call_next):
    # Check if the request is for a file or API endpoint
    response = await call_next(request)
    if response.status_code == 404 and not request.url.path.startswith("/api"):
        return FileResponse("http/public/index.html")
    return response


middleware = spa_redirect_middleware
