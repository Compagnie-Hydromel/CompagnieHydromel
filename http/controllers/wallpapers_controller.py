from fastapi import APIRouter
from fastapi.responses import FileResponse

from libs.storages.wallpaper_uploads import WallpaperUploads


router = APIRouter(prefix="/wallpapers")


@router.get("/{filename}")
async def image(filename: str):
    return FileResponse(WallpaperUploads.image_path(filename), media_type="image/png", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "X-Content-Type-Options": "nosniff",
    })
