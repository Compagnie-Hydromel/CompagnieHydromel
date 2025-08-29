import json
import traceback
from fastapi import Request
from starlette.responses import Response as HTTPResponse
from libs.log import Log


async def log_requests(request: Request, call_next):
    Log.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)

        Log.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        Log.error(f"Error processing request: " + traceback.format_exc())
        content = {"error": "Internal Server Error", "message": str(e)}
        return HTTPResponse(status_code=500, content=json.dumps(content), media_type="application/json")

middleware = log_requests
