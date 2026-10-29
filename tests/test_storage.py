import unittest
from unittest.mock import Mock, patch

from libs.storages.storage import Storage


class TestStorageURLFormat(unittest.TestCase):
    def test_discord_avatar_query_is_preserved_when_downloading(self):
        url = (
            "https://cdn.discordapp.com/guilds/928279859627696179/"
            "users/386200134628671492/avatars/"
            "a_32ae8ede980207a10cb9801eee58cfab.gif?size=1024"
        )
        with patch("libs.storages.https_storage.requests.get") as get:
            get.return_value.content = b"avatar"
            self.assertEqual(Storage().get(url), b"avatar")
        get.assert_called_once_with(url)
        get.return_value.raise_for_status.assert_called_once_with()

    def test_http_urls_keep_queries_and_fragments(self):
        for scheme in ("http", "https"):
            url = scheme + "://example.com:8080/image%20name.gif?size=1024&token=a%2Fb#preview"
            with self.subTest(scheme=scheme):
                self.assertEqual(Storage().get_path(url), url)
                self.assertEqual(Storage().get_file_type(url), "gif")

    def test_http_file_type_uses_only_the_url_path(self):
        for path, extension in (
            ("image.GIF?size=1024", "gif"),
            ("image.png?filename=other.gif#preview.jpg", "png"),
            ("image", ""),
        ):
            with self.subTest(path=path):
                self.assertEqual(Storage().get_file_type("https://example.com/" + path), extension)

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
        for url in ("://file.png", "local://", "local://file.png\n",
                    "https://", "https:///image.png", "https://example.com/image.png\n"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    Storage().get_path(url)
