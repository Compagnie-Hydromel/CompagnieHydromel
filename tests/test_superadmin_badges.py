from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from PIL import Image
from pydantic import ValidationError
from starlette.datastructures import FormData, UploadFile

from libs.storages.badge_uploads import BadgeUploads
from libs.utils.http_utils import HTTPUtils
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "superadmin_badges_controller", "http/controllers/superadmin_badges_controller.py")


def image_file():
    output = BytesIO()
    Image.new("RGBA", (64, 64), (255, 0, 0, 100)).save(output, format="PNG")
    return UploadFile(BytesIO(output.getvalue()), filename="badge.png")


class TestSuperadminAuthorization(unittest.TestCase):
    def test_guild_admin_is_not_automatically_superadmin(self):
        with patch.object(HTTPUtils, "get_user_from_session", return_value=SimpleNamespace(is_superadmin=False, is_admin=True)), self.assertRaises(HTTPException) as error:
            HTTPUtils.get_superadmin_from_session(Mock())
        self.assertEqual(error.exception.status_code, 403)

    def test_global_superadmin_is_authorized(self):
        user = SimpleNamespace(is_superadmin=True)
        with patch.object(HTTPUtils, "get_user_from_session", return_value=user):
            self.assertIs(HTTPUtils.get_superadmin_from_session(Mock()), user)

    def test_requires_login(self):
        with patch.object(HTTPUtils, "get_user_from_session", side_effect=HTTPException(401)), self.assertRaises(HTTPException) as error:
            HTTPUtils.get_superadmin_from_session(Mock())
        self.assertEqual(error.exception.status_code, 401)


class TestBadgeManagement(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.badge = SimpleNamespace(
            id=7, name="Hero", url="https://example.com/badge.png", saveOrFail=Mock(), delete=Mock())
        authorization = patch.object(
            HTTPUtils, "get_superadmin_from_session", return_value=SimpleNamespace(id=1))
        self.authorize = authorization.start()
        self.addCleanup(authorization.stop)
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "badges"
        directory = patch.object(BadgeUploads, "DIRECTORY", self.root)
        directory.start()
        self.addCleanup(directory.stop)

    async def test_all_mutations_require_superadmin(self):
        self.authorize.side_effect = HTTPException(403)
        calls = ((controller.index, (Mock(),)), (controller.users, (Mock(), "", 1)), (controller.create, (Mock(),)),
                 (controller.rename, (Mock(), 7, controller.BadgeWrite(
                     name="New"))), (controller.replace_image, (Mock(), 7)),
                 (controller.delete, (Mock(), 7)), (controller.assign, (Mock(), 7, 1)), (controller.revoke, (Mock(), 7, 1)))
        with patch.object(controller.Badge, "find") as lookup, patch.object(controller, "image_upload_form", new_callable=AsyncMock) as parse:
            for method, args in calls:
                with self.subTest(method=method.__name__), self.assertRaises(HTTPException):
                    await method(*args)
        lookup.assert_not_called()
        parse.assert_not_awaited()

    async def test_create_upload_normalizes_image_and_preserves_transparency(self):
        form = FormData({"name": "Hero", "image": image_file()})
        with patch.object(controller, "image_upload_form", new_callable=AsyncMock, return_value=form), patch.object(
            controller.Badge, "whereFirst", return_value=None
        ), patch.object(controller.Badge, "createOrFail", side_effect=lambda **attributes: SimpleNamespace(id=7, **attributes)):
            result = await controller.create(Mock())
        self.assertTrue(result["url"].startswith("/api/badge-images/1-"))
        with Image.open(next(self.root.iterdir())) as image:
            self.assertEqual(image.size, (128, 128))
            self.assertEqual(image.getpixel((0, 0))[3], 100)

    async def test_rename_preserves_id_and_image(self):
        with patch.object(controller.Badge, "find", return_value=self.badge), patch.object(controller.Badge, "whereFirst", return_value=None):
            result = await controller.rename(Mock(), 7, controller.BadgeWrite(name="Champion"))
        self.assertEqual(
            result, {"id": 7, "name": "Champion", "url": "https://example.com/badge.png"})

    async def test_duplicate_name_is_rejected(self):
        with patch.object(controller.Badge, "find", return_value=self.badge), patch.object(
            controller.Badge, "whereFirst", return_value=SimpleNamespace(id=8)
        ), self.assertRaises(HTTPException) as error:
            await controller.rename(Mock(), 7, controller.BadgeWrite(name="Existing"))
        self.assertEqual(error.exception.status_code, 409)
        self.badge.saveOrFail.assert_not_called()

    async def test_replace_image_preserves_identity(self):
        form = FormData({"image": image_file()})
        with patch.object(controller.Badge, "find", return_value=self.badge), patch.object(
            controller, "image_upload_form", new_callable=AsyncMock, return_value=form
        ):
            result = await controller.replace_image(Mock(), 7)
        self.assertEqual(result["id"], 7)
        self.assertEqual(result["name"], "Hero")
        self.assertTrue(result["url"].startswith("/api/badge-images/"))

    async def test_failed_save_removes_only_new_upload(self):
        self.badge.saveOrFail.side_effect = RuntimeError("database failed")
        with patch.object(controller.Badge, "find", return_value=self.badge), patch.object(
            controller, "image_upload_form", new_callable=AsyncMock, return_value=FormData({"image": image_file()})
        ), self.assertRaises(RuntimeError):
            await controller.replace_image(Mock(), 7)
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(self.badge.url, "https://example.com/badge.png")

    async def test_assignment_is_idempotent(self):
        user = SimpleNamespace(badges=[])
        with patch.object(controller.Badge, "find", return_value=self.badge), patch.object(controller.User, "find", return_value=user):
            await controller.assign(Mock(), 7, 1)
            await controller.assign(Mock(), 7, 1)
        self.assertEqual(user.badges, [self.badge])

    async def test_revoke_removes_legacy_duplicates_but_keeps_other_badges(self):
        other = SimpleNamespace(id=8)
        user = SimpleNamespace(badges=[self.badge, self.badge, other])
        with patch.object(controller.Badge, "find", return_value=self.badge), patch.object(controller.User, "find", return_value=user):
            await controller.revoke(Mock(), 7, 1)
        self.assertEqual(user.badges, [other])

    async def test_delete_badge(self):
        with patch.object(controller.Badge, "find", return_value=self.badge):
            await controller.delete(Mock(), 7)
        self.badge.delete.assert_called_once_with()

    async def test_missing_badge_is_404(self):
        with patch.object(controller.Badge, "find", return_value=None), self.assertRaises(HTTPException) as error:
            await controller.delete(Mock(), 7)
        self.assertEqual(error.exception.status_code, 404)

    def test_name_and_extra_privilege_fields_are_validated(self):
        for data in ({"name": " "}, {"name": "a" * 81}, {"name": "Hero", "is_superadmin": True}):
            with self.subTest(data=data), self.assertRaises(ValidationError):
                controller.BadgeWrite(**data)
