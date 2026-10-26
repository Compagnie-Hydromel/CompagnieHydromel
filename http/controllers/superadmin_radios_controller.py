from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from libs.databases.models.radio import Radio
from libs.music.music_manager import public_url
from libs.utils.http_utils import HTTPUtils


router = APIRouter(prefix="/superadmin/radios")


class RadioWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1, max_length=255)


def radio_data(radio):
    return {"id": radio.id, "slug": radio.slug, "name": radio.name, "url": radio.url}


def find_radio(radio_id):
    radio = Radio.find(radio_id)
    if radio is None:
        raise HTTPException(404, "Radio introuvable.")
    return radio


async def validate(changes, current=None):
    duplicate = Radio.whereFirst(name=changes.name)
    if duplicate is not None and (current is None or duplicate.id != current.id):
        raise HTTPException(409, "Une radio porte déjà ce nom.")
    try:
        await run_in_threadpool(public_url, changes.url)
    except (ValueError, OSError):
        raise HTTPException(422, "Utilisez une URL de flux HTTP(S) publique, sans identifiants ni adresse privée.")


@router.get("")
async def index(request: Request):
    HTTPUtils.get_superadmin_from_session(request)
    return [radio_data(radio) for radio in sorted(Radio.all(), key=lambda radio: radio.name.casefold())]


@router.post("", status_code=201)
async def create(request: Request, changes: RadioWrite):
    HTTPUtils.get_superadmin_from_session(request)
    await validate(changes)
    radio = Radio.createOrFail(slug="radio-" + uuid4().hex, **changes.model_dump())
    return radio_data(radio)


@router.patch("/{radio_id}")
async def update(request: Request, radio_id: Annotated[int, Path(gt=0)], changes: RadioWrite):
    HTTPUtils.get_superadmin_from_session(request)
    radio = find_radio(radio_id)
    await validate(changes, radio)
    radio.name, radio.url = changes.name, changes.url
    radio.saveOrFail()
    return radio_data(radio)


@router.delete("/{radio_id}")
async def delete(request: Request, radio_id: Annotated[int, Path(gt=0)]):
    HTTPUtils.get_superadmin_from_session(request)
    find_radio(radio_id).delete()
    return {"deleted": True}
