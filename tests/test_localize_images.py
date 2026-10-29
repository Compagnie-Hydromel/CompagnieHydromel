from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PIL import Image

from commands.localize_images import download, localize
from libs.storages.badge_uploads import BadgeUploads
from libs.storages.wallpaper_uploads import WallpaperUploads


class TestLocalizeImages(unittest.TestCase):
    def test_migrates_both_types_and_can_be_rerun(self):
        output = BytesIO()
        Image.new("RGB", (100, 100), "red").save(output, format="PNG")
        for uploads in (WallpaperUploads, BadgeUploads):
            with self.subTest(uploads=uploads), TemporaryDirectory() as directory:
                record = SimpleNamespace(id=1, url="https://example.com/image.png", saveOrFail=Mock())
                with patch.object(uploads, "DIRECTORY", Path(directory)), patch(
                        "commands.localize_images.download", return_value=output.getvalue()) as fetch:
                    self.assertEqual(localize([record], uploads, "images"), 0)
                    self.assertTrue(record.url.startswith(uploads.PREFIX))
                    self.assertEqual(len(list(Path(directory).iterdir())), 1)
                    self.assertEqual(localize([record], uploads, "images"), 0)
                    fetch.assert_called_once()
                    record.saveOrFail.assert_called_once()

    def test_failed_save_restores_url_and_removes_new_file(self):
        record = SimpleNamespace(id=1, url="http://example.com/image.png",
                                 saveOrFail=Mock(side_effect=RuntimeError("Database unavailable")))
        uploads = Mock(MAX_BYTES=1024)
        uploads.store.return_value = "local://badges/new.png"
        with patch("commands.localize_images.download", return_value=b"image"):
            self.assertEqual(localize([record], uploads, "badges"), 1)
        self.assertEqual(record.url, "http://example.com/image.png")
        uploads.delete.assert_called_once_with("local://badges/new.png")

    def test_download_failure_continues_without_changes(self):
        records = [SimpleNamespace(id=i, url="https://example.com/image.png", saveOrFail=Mock())
                   for i in (1, 2)]
        with patch("commands.localize_images.download", side_effect=ValueError("Invalid image")) as fetch:
            self.assertEqual(localize(records, Mock(), "badges"), 2)
        self.assertEqual(fetch.call_count, 2)
        for record in records:
            record.saveOrFail.assert_not_called()
            self.assertEqual(record.url, "https://example.com/image.png")

    def test_dry_run_does_not_download_or_save(self):
        record = SimpleNamespace(id=1, url="https://example.com/image.png", saveOrFail=Mock())
        with patch("commands.localize_images.download") as fetch:
            self.assertEqual(localize([record], Mock(), "badges", dry_run=True), 0)
        fetch.assert_not_called()
        record.saveOrFail.assert_not_called()

    def test_download_limits_stream_and_closes_response(self):
        response = Mock(url="https://example.com/image.png")
        response.iter_content.return_value = [b"123", b"456"]
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        with patch("commands.localize_images.requests.get", return_value=context):
            with self.assertRaisesRegex(ValueError, "exceeds"):
                download(response.url, 5)
        context.__exit__.assert_called_once()
