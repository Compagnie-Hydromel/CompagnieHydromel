from pydantic import BaseModel

from libs.databases.models.wallpaper import Wallpaper
from libs.storages.wallpaper_uploads import WallpaperUploads


class WallpaperProjection(BaseModel):
    id: int | None
    name: str
    url: str

    @classmethod
    def from_wallpaper(cls, wallpaper: Wallpaper):
        return cls(id=wallpaper.id,
                   name=wallpaper.name,
                   url=WallpaperUploads.public_url(wallpaper.url))
