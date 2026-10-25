import json
import traceback
from fastapi import Request
import mysql
from starlette.responses import Response as HTTPResponse
from libs.log import Log
from MIWOS.libs.exceptions.not_found_exception import NotFoundException
from MIWOS.libs.exceptions.validation_exception import ValidationException
from MIWOS.libs.exceptions.MIWOS_exception import MIWOSException


async def log_requests(request: Request, call_next):
    Log.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)

        Log.info(f"Response status: {response.status_code}")
        return response
    except NotFoundException as e:
        Log.info(f"Not Found: {str(e)}")
        return HTTPResponse(status_code=404, content=json.dumps({"error": "Not Found", "message": str(e)}), media_type="application/json")
    except ValidationException as e:
        Log.info(f"Validation Error: {str(e)}")
        return HTTPResponse(status_code=400, content=json.dumps({"error": "Bad Request", "message": str(e)}), media_type="application/json")
    except MIWOSException as e:
        Log.error(f"MIWOS Exception: {str(e)}")
        return HTTPResponse(status_code=500, content=json.dumps({"error": "Internal Server Error", "message": str(e)}), media_type="application/json")
    except mysql.connector.errors.DatabaseError as e:
        Log.error(f"MySQL Database Error: {str(e)}")
        return HTTPResponse(status_code=500, content=json.dumps({"error": "Database Error", "message": str(e)}), media_type="application/json")
    except Exception as e:
        Log.error(f"Error processing request: " + traceback.format_exc())
        content = {"error": "Internal Server Error", "message": str(e)}
        return HTTPResponse(status_code=500, content=json.dumps(content), media_type="application/json")

middleware = log_requests
