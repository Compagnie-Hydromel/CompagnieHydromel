from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from libs.databases.models.user import User

router = APIRouter(prefix="/users")


@router.get("")
async def all(request: Request):
    user = User.all()
    user_list = [u.to_dict() for u in user]
    return user_list
