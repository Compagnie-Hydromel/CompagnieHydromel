from pathlib import Path

from libs.storages.wallpaper_uploads import WallpaperUploads


class BadgeUploads(WallpaperUploads):
    DIRECTORY = Path("storages/locals/badges")
    PREFIX = "local://badges/"
    PUBLIC_PREFIX = "/api/badge-images/"
    SIZE = (128, 128)
