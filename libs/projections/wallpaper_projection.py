from pydantic import BaseModel

from libs.databases.models.wallpaper import Wallpaper


class WallpaperProjection(BaseModel):
    id: int | None
    name: str
    url: str

    @classmethod
    def from_wallpaper(cls, wallpaper: Wallpaper):
        return cls(id=wallpaper.id,
                   name=wallpaper.name,
                   url=wallpaper.url)
