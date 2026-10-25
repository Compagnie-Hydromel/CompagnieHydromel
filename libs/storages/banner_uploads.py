from pathlib import Path

from libs.storages.wallpaper_uploads import WallpaperUploads


class BannerUploads(WallpaperUploads):
    DIRECTORY = Path("storages/locals/banners")
    PREFIX = "local://banners/"
    PUBLIC_PREFIX = "/api/banners/"
    SIZE = (960, 540)
