from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from libs.utils.utils import Utils


controller = Utils.import_module_from_path("superadmin_radios_controller", "http/controllers/superadmin_radios_controller.py")


class TestRadioManagement(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.radio = SimpleNamespace(id=1, slug="fip", name="FIP", url="https://radio.example/live.mp3", saveOrFail=Mock(), delete=Mock())
        authorization = patch.object(controller.HTTPUtils, "get_superadmin_from_session", return_value=SimpleNamespace(id=1))
        self.authorize = authorization.start()
        self.addCleanup(authorization.stop)

    async def test_reads_and_mutations_require_superadmin_before_database_access(self):
        self.authorize.side_effect = HTTPException(403)
        changes = controller.RadioWrite(name="Radio", url="https://radio.example/live.mp3")
        with patch.object(controller.Radio, "find") as find, patch.object(controller.Radio, "all") as all_radios, patch.object(controller.Radio, "whereFirst") as duplicate:
            for method, args in ((controller.index, (Mock(),)), (controller.create, (Mock(), changes)),
                                 (controller.update, (Mock(), 1, changes)), (controller.delete, (Mock(), 1))):
                with self.assertRaises(HTTPException):
                    await method(*args)
        find.assert_not_called()
        all_radios.assert_not_called()
        duplicate.assert_not_called()

    async def test_create_stores_named_station_with_server_generated_id(self):
        changes = controller.RadioWrite(name="Jazz", url="https://radio.example/jazz.mp3")
        with patch.object(controller.Radio, "whereFirst", return_value=None), patch.object(
            controller, "public_url", side_effect=lambda url: url
        ) as validate, patch.object(controller.Radio, "createOrFail", side_effect=lambda **values: SimpleNamespace(id=2, **values)):
            result = await controller.create(Mock(), changes)
        self.assertEqual(result["name"], "Jazz")
        self.assertEqual(result["url"], changes.url)
        self.assertTrue(result["slug"].startswith("radio-"))
        validate.assert_called_once_with(changes.url)

    async def test_update_preserves_selection_id(self):
        with patch.object(controller.Radio, "find", return_value=self.radio), patch.object(controller.Radio, "whereFirst", return_value=self.radio), patch.object(controller, "public_url", side_effect=lambda url: url):
            result = await controller.update(Mock(), 1, controller.RadioWrite(name="Renamed", url="https://radio.example/new.mp3"))
        self.assertEqual(result["slug"], "fip")
        self.assertEqual(result["name"], "Renamed")
        self.radio.saveOrFail.assert_called_once()

    async def test_duplicate_name_is_rejected(self):
        with patch.object(controller.Radio, "whereFirst", return_value=self.radio), patch.object(controller.Radio, "createOrFail") as create, self.assertRaises(HTTPException) as error:
            await controller.create(Mock(), controller.RadioWrite(name="FIP", url=self.radio.url))
        self.assertEqual(error.exception.status_code, 409)
        create.assert_not_called()

    async def test_private_stream_destination_is_rejected(self):
        with patch.object(controller.Radio, "whereFirst", return_value=None), patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("127.0.0.1", 80))]), patch.object(controller.Radio, "createOrFail") as create, self.assertRaises(HTTPException) as error:
            await controller.create(Mock(), controller.RadioWrite(name="Private", url="http://example.com/live"))
        self.assertEqual(error.exception.status_code, 422)
        create.assert_not_called()

    async def test_non_http_and_credential_urls_are_rejected(self):
        for url in ("file:///etc/passwd", "ftp://example.com/audio", "https://user:pass@example.com/audio"):
            with patch.object(controller.Radio, "whereFirst", return_value=None), self.assertRaises(HTTPException) as error:
                await controller.create(Mock(), controller.RadioWrite(name="Radio", url=url))
            self.assertEqual(error.exception.status_code, 422)

    async def test_delete_removes_station(self):
        with patch.object(controller.Radio, "find", return_value=self.radio):
            self.assertEqual(await controller.delete(Mock(), 1), {"deleted": True})
        self.radio.delete.assert_called_once()

    async def test_unknown_station_returns_404(self):
        with patch.object(controller.Radio, "find", return_value=None), self.assertRaises(HTTPException) as error:
            await controller.delete(Mock(), 99)
        self.assertEqual(error.exception.status_code, 404)

    def test_input_validation_rejects_empty_names_and_extra_ids(self):
        for values in ({"name": " ", "url": self.radio.url}, {"name": "Radio", "url": self.radio.url, "slug": "forced"},
                       {"name": "Radio", "url": "https://example.com/" + "x" * 255}):
            with self.assertRaises(ValidationError):
                controller.RadioWrite(**values)
