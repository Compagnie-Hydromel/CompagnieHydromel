from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile

from libs.databases.models.badge import Badge
from libs.databases.models.user import User
from libs.storages.badge_uploads import BadgeUploads
from libs.utils.http_utils import HTTPUtils
from libs.utils.upload_utils import image_upload_form


router = APIRouter(prefix="/superadmin/badges")


class BadgeWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=80)


def badge_data(badge):
    return {"id": badge.id, "name": badge.name, "url": BadgeUploads.public_url(badge.url)}


def find_badge(id):
    badge = Badge.find(id)
    if badge is None:
        raise HTTPException(
            status_code=404, detail="superadmin.badges.missing")
    return badge


def unique_name(name, current=None):
    duplicate = Badge.whereFirst(name=name)
    if duplicate is not None and (current is None or duplicate.id != current.id):
        raise HTTPException(
            status_code=409, detail="superadmin.badges.duplicate")


@router.get("")
async def index(request: Request):
    HTTPUtils.get_superadmin_from_session(request)
    return [badge_data(badge) for badge in Badge.all()]


@router.get("/users")
async def users(request: Request, search: str = Query(default="", max_length=100), page: int = Query(default=1, ge=1)):
    HTTPUtils.get_superadmin_from_session(request)
    # Search by stored Discord ID; names are resolved from the bot cache only.
    matches = [user for user in User.all() if search.strip()
               in str(user.discord_id)]
    result = []
    for user in matches[(page - 1) * 20:page * 20]:
        bot = getattr(User, "bot", None)
        discord_user = bot.get_user(int(user.discord_id)) if bot else None
        result.append({"id": user.id, "discord_id": str(user.discord_id),
                       "name": discord_user.display_name if discord_user else str(user.discord_id),
                       "badges": [badge_data(badge) for badge in user.badges]})
    return {"users": result, "total": len(matches), "page": page}


@router.post("", status_code=201)
async def create(request: Request):
    actor = HTTPUtils.get_superadmin_from_session(request)
    form = await image_upload_form(request, BadgeUploads.MAX_BYTES, max_fields=1)
    try:
        if len(form.multi_items()) != 2 or set(form) != {"name", "image"} or not isinstance(form["image"], UploadFile):
            raise HTTPException(
                status_code=422, detail="superadmin.badges.invalid")
        name = form["name"]
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
            raise HTTPException(
                status_code=422, detail="superadmin.badges.invalid")
        unique_name(name.strip())
        content = await form["image"].read(BadgeUploads.MAX_BYTES + 1)
        url = await run_in_threadpool(BadgeUploads.store, content, actor.id)
        try:
            badge = Badge.createOrFail(name=name.strip(), url=url)
        except Exception:
            BadgeUploads.delete(url)
            raise
        return badge_data(badge)
    finally:
        await form.close()


@router.patch("/{badge_id}")
async def rename(request: Request, badge_id: Annotated[int, Path(gt=0)], changes: BadgeWrite):
    HTTPUtils.get_superadmin_from_session(request)
    badge = find_badge(badge_id)
    unique_name(changes.name, badge)
    badge.name = changes.name
    badge.saveOrFail()
    return badge_data(badge)


@router.post("/{badge_id}/image")
async def replace_image(request: Request, badge_id: Annotated[int, Path(gt=0)]):
    actor = HTTPUtils.get_superadmin_from_session(request)
    badge = find_badge(badge_id)
    form = await image_upload_form(request, BadgeUploads.MAX_BYTES, max_fields=0)
    try:
        if len(form.multi_items()) != 1 or not isinstance(form.get("image"), UploadFile):
            raise HTTPException(
                status_code=422, detail="superadmin.badges.invalid")
        url = await run_in_threadpool(BadgeUploads.store, await form["image"].read(BadgeUploads.MAX_BYTES + 1), actor.id)
        previous = badge.url
        try:
            badge.url = url
            badge.saveOrFail()
        except Exception:
            badge.url = previous
            BadgeUploads.delete(url)
            raise
        return badge_data(badge)
    finally:
        await form.close()


@router.delete("/{badge_id}")
async def delete(request: Request, badge_id: Annotated[int, Path(gt=0)]):
    HTTPUtils.get_superadmin_from_session(request)
    find_badge(badge_id).delete()
    return {"deleted": True}


@router.post("/{badge_id}/users/{user_id}")
async def assign(request: Request, badge_id: Annotated[int, Path(gt=0)], user_id: Annotated[int, Path(gt=0)]):
    HTTPUtils.get_superadmin_from_session(request)
    badge = find_badge(badge_id)
    user = User.find(user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail="superadmin.badges.missingUser")
    if not any(item.id == badge.id for item in user.badges):
        user.badges.append(badge)
    return {"assigned": True}


@router.delete("/{badge_id}/users/{user_id}")
async def revoke(request: Request, badge_id: Annotated[int, Path(gt=0)], user_id: Annotated[int, Path(gt=0)]):
    HTTPUtils.get_superadmin_from_session(request)
    find_badge(badge_id)
    user = User.find(user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail="superadmin.badges.missingUser")
    collection = user.badges
    # Legacy assignments can contain duplicates; revoke every occurrence.
    for badge in list(collection):
        if badge.id == badge_id:
            collection.remove(badge)
    return {"assigned": False}
