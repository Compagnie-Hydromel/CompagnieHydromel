from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from starlette.requests import Request

from libs.projections.wallpaper_projection import WallpaperProjection
from libs.storages.local_storage import LocalStorage
from libs.storages.storage import Storage
from libs.storages.wallpaper_uploads import WallpaperUploads
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "upload_admin_controller", "http/controllers/guild_admin_controller.py")
media = Utils.import_module_from_path(
    "wallpapers_controller", "http/controllers/wallpapers_controller.py")


def image_bytes(format="PNG"):
    output = BytesIO()
    Image.new("RGB", (100, 100), "red").save(output, format=format)
    return output.getvalue()


def multipart_request(content, fields=None, filename="../../untrusted.png", extra_files=0):
    boundary = "wallpaper-test-boundary"
    body = b""
    for name, value in (fields if fields is not None else {"name": "Forest", "price": "25", "level": "0"}).items():
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n').encode()
    for index in range(extra_files + 1):
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{filename}"\r\nContent-Type: image/png\r\n\r\n').encode()
        body += content + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    sent = False

    async def receive():
        nonlocal sent
        if sent:
            return {"type": "http.disconnect"}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    return Request({"type": "http", "method": "POST", "headers": [
        (b"content-type", f"multipart/form-data; boundary={boundary}".encode())
    ]}, receive)


class TestWallpaperStorage(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "wallpapers"
        patcher = patch.object(WallpaperUploads, "DIRECTORY", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_valid_images_are_normalized_and_work_with_discord_storage(self):
        for format in ("PNG", "JPEG", "WEBP"):
            with self.subTest(format=format):
                url = WallpaperUploads.store(image_bytes(format), 10)
                filename = url.removeprefix(WallpaperUploads.PREFIX)
                with Image.open(WallpaperUploads.image_path(filename)) as image:
                    self.assertEqual(image.size, (500, 281))
                    self.assertEqual(image.format, "PNG")
                local = LocalStorage(self.directory.name)
                with patch("libs.storages.local_storage.LocalStorage", return_value=local):
                    self.assertTrue(Storage().get(url).startswith(b"\x89PNG"))

    def test_image_bytes_are_validated_not_just_extension_or_mime(self):
        for data in (b"", b"<svg onload='alert(1)'></svg>", b"not an image", image_bytes("GIF")):
            with self.subTest(data=data[:20]), self.assertRaises(HTTPException) as error:
                WallpaperUploads.store(data, 10)
            self.assertEqual(error.exception.status_code, 422)
        self.assertFalse(self.root.exists())

    def test_size_and_pixel_limits(self):
        with patch.object(WallpaperUploads, "MAX_BYTES", 10), self.assertRaises(HTTPException) as error:
            WallpaperUploads.store(image_bytes(), 10)
        self.assertEqual(error.exception.status_code, 413)
        with patch.object(WallpaperUploads, "MAX_PIXELS", 10), self.assertRaises(HTTPException) as error:
            WallpaperUploads.store(image_bytes(), 10)
        self.assertEqual(error.exception.status_code, 422)

    def test_public_url_projection_does_not_expose_local_storage_scheme(self):
        url = WallpaperUploads.store(image_bytes(), 10)
        wallpaper = SimpleNamespace(id=1, name="Forest", url=url)
        projection = WallpaperProjection.from_wallpaper(wallpaper)
        self.assertTrue(projection.url.startswith("/api/wallpapers/10-"))
        self.assertEqual(WallpaperUploads.public_url(
            "https://example.com/image.png"), "https://example.com/image.png")

    def test_images_have_unique_server_generated_names(self):
        first = WallpaperUploads.store(image_bytes(), 10)
        second = WallpaperUploads.store(image_bytes(), 10)
        self.assertNotEqual(first, second)
        WallpaperUploads.delete(first)
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_uploaded_image_metadata_is_removed(self):
        output = BytesIO()
        metadata = PngInfo()
        metadata.add_text("private", "should not be published")
        Image.new("RGB", (100, 100), "red").save(
            output, format="PNG", pnginfo=metadata)
        url = WallpaperUploads.store(output.getvalue(), 10)
        with Image.open(self.root / url.removeprefix(WallpaperUploads.PREFIX)) as image:
            self.assertNotIn("private", image.info)

    def test_filename_collision_does_not_overwrite_or_delete_existing_image(self):
        self.root.mkdir()
        path = self.root / ("10-" + "a" * 32 + ".png")
        path.write_bytes(b"existing image")
        with patch("libs.storages.wallpaper_uploads.uuid4", return_value=SimpleNamespace(hex="a" * 32)), self.assertRaises(FileExistsError):
            WallpaperUploads.store(image_bytes(), 10)
        self.assertEqual(path.read_bytes(), b"existing image")

    def test_image_route_rejects_traversal_and_missing_files(self):
        for filename in ("../../.env", "test.svg", "10-" + "a" * 32 + ".png"):
            with self.subTest(filename=filename), self.assertRaises(HTTPException) as error:
                WallpaperUploads.image_path(filename)
            self.assertEqual(error.exception.status_code, 404)


class TestWallpaperUploadEndpoint(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "wallpapers"
        directory = patch.object(WallpaperUploads, "DIRECTORY", self.root)
        directory.start()
        self.addCleanup(directory.stop)
        permission = patch.object(controller.HTTPUtils, "get_guild_admin_from_session",
                                  new_callable=AsyncMock, return_value=SimpleNamespace(id=10))
        self.authorize = permission.start()
        self.addCleanup(permission.stop)
        existing = patch.object(controller.Wallpaper,
                                "whereFirst", return_value=None)
        existing.start()
        self.addCleanup(existing.stop)

    async def test_real_multipart_upload_persists_image_and_returns_public_url(self):
        def create(**attributes):
            return SimpleNamespace(id=1, **attributes)

        with patch.object(controller.Wallpaper, "createOrFail", side_effect=create) as save:
            result = await controller.create_wallpaper(multipart_request(image_bytes()), 10)
        self.assertEqual(result["price"], 25)
        self.assertEqual(result["name"], "Forest")
        self.assertTrue(result["url"].startswith("/api/wallpapers/10-"))
        self.assertTrue(save.call_args.kwargs["url"].startswith(
            "local://wallpapers/10-"))
        self.assertEqual(len(list(self.root.iterdir())), 1)
        response = await media.image(result["url"].rsplit("/", 1)[1])
        self.assertEqual(response.media_type, "image/png")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")

    async def test_authorization_happens_before_reading_upload(self):
        self.authorize.side_effect = HTTPException(403)
        with patch.object(controller, "wallpaper_form", new_callable=AsyncMock) as parse, self.assertRaises(HTTPException):
            await controller.create_wallpaper(multipart_request(image_bytes()), 10)
        parse.assert_not_awaited()
        self.assertFalse(self.root.exists())

    async def test_invalid_metadata_and_files_are_rejected_without_persisting(self):
        cases = [(b"fake image", None), (image_bytes(), {"name": "", "price": "25", "level": "0"}),
                 (image_bytes(), {"name": "Forest",
                  "price": "-1", "level": "0"}),
                 (image_bytes(), {"name": "Forest", "price": "25"})]
        for content, fields in cases:
            with self.subTest(fields=fields), patch.object(controller.Wallpaper, "createOrFail") as save, self.assertRaises(HTTPException) as error:
                await controller.create_wallpaper(multipart_request(content, fields), 10)
            self.assertEqual(error.exception.status_code, 422)
            save.assert_not_called()
        self.assertFalse(self.root.exists())

    async def test_extra_files_are_rejected(self):
        with self.assertRaises(HTTPException) as error:
            await controller.create_wallpaper(multipart_request(image_bytes(), extra_files=1), 10)
        self.assertEqual(error.exception.status_code, 400)

    async def test_request_stream_is_bounded(self):
        with patch.object(WallpaperUploads, "MAX_BYTES", 10), self.assertRaises(HTTPException) as error:
            await controller.create_wallpaper(multipart_request(b"a" * 70000), 10)
        self.assertEqual(error.exception.status_code, 413)

    async def test_individual_file_size_limit_is_enforced(self):
        with patch.object(WallpaperUploads, "MAX_BYTES", 10), self.assertRaises(HTTPException) as error:
            await controller.create_wallpaper(multipart_request(image_bytes()), 10)
        self.assertEqual(error.exception.status_code, 413)
        self.assertFalse(self.root.exists())

    async def test_database_failure_removes_just_uploaded_image(self):
        with patch.object(controller.Wallpaper, "createOrFail", side_effect=RuntimeError("database failed")), self.assertRaisesRegex(RuntimeError, "database failed"):
            await controller.create_wallpaper(multipart_request(image_bytes()), 10)
        self.assertEqual(list(self.root.iterdir()), [])

    async def test_old_json_url_input_is_not_accepted(self):
        request = Request({"type": "http", "headers": [
                          (b"content-type", b"application/json")]})
        with self.assertRaises(HTTPException) as error:
            await controller.create_wallpaper(request, 10)
        self.assertEqual(error.exception.status_code, 415)
