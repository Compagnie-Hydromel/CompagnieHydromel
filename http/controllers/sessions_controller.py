from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from libs.databases.models.user import User

router = APIRouter(prefix="/sessions")


@router.get("")
async def one(request: Request):
    if "authorization" in request.query_params:
        user = User.verify_authorization_token(
            request.query_params["authorization"]
        )
        if not user:
            return RedirectResponse(url="/")
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard")

    user = User.find(request.session.get("user_id", None))
    if not user:
        raise HTTPException(status_code=401, detail="No active session found.")
    return {"user": user.to_dict()}


@router.delete("")
async def delete(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(status_code=401, detail="No active session found.")
    request.session.clear()
    return {"message": "Logged out successfully"}
