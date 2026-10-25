from fastapi import APIRouter
from fastapi.responses import FileResponse

from libs.storages.banner_uploads import BannerUploads


router = APIRouter(prefix="/banners")


@router.get("/{filename}")
async def image(filename: str):
    return FileResponse(BannerUploads.image_path(filename), media_type="image/png", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "X-Content-Type-Options": "nosniff",
    })
