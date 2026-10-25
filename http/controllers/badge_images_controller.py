from fastapi import APIRouter
from fastapi.responses import FileResponse

from libs.storages.badge_uploads import BadgeUploads


router = APIRouter(prefix="/badge-images")


@router.get("/{filename}")
async def image(filename: str):
    return FileResponse(BadgeUploads.image_path(filename), media_type="image/png", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "X-Content-Type-Options": "nosniff",
    })
