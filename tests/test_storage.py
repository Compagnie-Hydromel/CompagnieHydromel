import unittest
from unittest.mock import Mock, patch

from libs.storages.storage import Storage


class TestStorageURLFormat(unittest.TestCase):
    def test_valid_paths_keep_digits_and_literal_punctuation(self):
        for url, scheme, path in (
            ("local://wallpapers/10-abc_123.png", "local", "wallpapers/10-abc_123.png"),
            ("caches://image éàè,!~.png", "caches", "image éàè,!~.png"),
            ("https://example.com/image-42.png", "https", "example.com/image-42.png"),
        ):
            with self.subTest(url=url):
                backend = Mock()
                with patch.object(Storage, "_Storage__get_storage_instance", return_value=backend) as resolve:
                    Storage().get_path(url)
                resolve.assert_called_once_with(scheme)
                backend.get_path.assert_called_once_with(path)

    def test_unintended_range_characters_are_rejected(self):
        for character in ":;<=>?@[\\]^":
            with self.subTest(character=character):
                with self.assertRaises(ValueError):
                    Storage().get_path("local://file" + character + ".png")

    def test_empty_parts_and_trailing_newline_are_rejected(self):
        for url in ("://file.png", "local://", "local://file.png\n"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    Storage().get_path(url)
