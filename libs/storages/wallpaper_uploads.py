from io import BytesIO
from pathlib import Path
import re
import warnings
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError


class WallpaperUploads:
    DIRECTORY = Path("storages/locals/wallpapers")
    MAX_BYTES = 8 * 1024 * 1024
    MAX_PIXELS = 16000000
    FILENAME = re.compile(r"[1-9][0-9]*-[0-9a-f]{32}\.png")
    PREFIX = "local://wallpapers/"
    PUBLIC_PREFIX = "/api/wallpapers/"
    SIZE = (500, 281)

    @classmethod
    def public_url(cls, url):
        if url.startswith(cls.PREFIX):
            filename = url[len(cls.PREFIX):]
            if cls.FILENAME.fullmatch(filename):
                return cls.PUBLIC_PREFIX + filename
        return url

    @classmethod
    def store(cls, data, guild_id):
        if len(data) > cls.MAX_BYTES:
            raise HTTPException(status_code=413, detail="Image exceeds 8 MiB")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(data)) as source:
                    if source.format not in ("PNG", "JPEG", "WEBP") or getattr(source, "is_animated", False):
                        raise ValueError(
                            "Use a static PNG, JPEG or WebP image")
                    if source.width * source.height > cls.MAX_PIXELS:
                        raise ValueError("Image exceeds 16 megapixels")
                    source.load()
                    image = ImageOps.fit(ImageOps.exif_transpose(source).convert("RGBA"),
                                         cls.SIZE, method=Image.Resampling.LANCZOS)
                    image.info.clear()
                    output = BytesIO()
                    image.save(output, format="PNG")
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise HTTPException(
                status_code=422, detail="Use a valid static PNG, JPEG or WebP image (max 16 megapixels)")

        cls.DIRECTORY.mkdir(parents=True, exist_ok=True)
        filename = f"{guild_id}-{uuid4().hex}.png"
        path = cls.DIRECTORY / filename
        created = False
        try:
            with path.open("xb") as file:
                created = True
                file.write(output.getvalue())
        except OSError:
            if created:
                path.unlink(missing_ok=True)
            raise
        return cls.PREFIX + filename

    @classmethod
    def delete(cls, url):
        filename = url.removeprefix(cls.PREFIX)
        if url.startswith(cls.PREFIX) and cls.FILENAME.fullmatch(filename):
            (cls.DIRECTORY / filename).unlink(missing_ok=True)

    @classmethod
    def image_path(cls, filename):
        if not cls.FILENAME.fullmatch(filename):
            raise HTTPException(status_code=404, detail="Image not found")
        path = cls.DIRECTORY / filename
        if path.is_symlink() or not path.is_file():
            raise HTTPException(status_code=404, detail="Image not found")
        return path
