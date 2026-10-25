from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError
from starlette.datastructures import FormData, UploadFile

from cogs.barman.admin_commands import AdminCommands
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "guild_messages_controller", "http/controllers/guild_messages_controller.py")


def payload(**changes):
    return controller.MessageWrite(**{"name": "Reminder", "channel_id": "100", "message": "Hello\nworld",
                                      "day": "daily", "time": "18:00", "timezone": "Europe/Zurich", **changes})


def record():
    return SimpleNamespace(id=7, **payload().model_dump(), last_sent_date="2026-10-25", attachment_path=None,
                           attachment_name=None, saveOrFail=Mock(), delete=Mock())


class TestAutomaticMessagesWeb(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.guild = SimpleNamespace(id=10)
        self.permissions = SimpleNamespace(
            view_channel=True, send_messages=True, attach_files=True)
        self.discord_guild = SimpleNamespace(me=Mock(), text_channels=[SimpleNamespace(
            id=100, name="news", permissions_for=lambda member: self.permissions)])
        context = patch.object(controller, "message_context", new_callable=AsyncMock, return_value=(
            self.guild, self.discord_guild))
        self.context = context.start()
        self.addCleanup(context.stop)
        self.record = record()

    async def test_lists_existing_schedules_for_current_guild(self):
        with patch.object(controller.ScheduledMessage, "where", return_value=[self.record]) as query:
            result = await controller.index(Mock(), 10)
        query.assert_called_once_with(guild=self.guild)
        self.assertEqual(result["messages"][0]["channel_name"], "news")
        self.assertEqual(result["messages"][0]["last_sent_date"], "2026-10-25")
        self.assertIn("Europe/Zurich", result["timezones"])

    async def test_creates_message_in_authorized_guild(self):
        with patch.object(controller.ScheduledMessage, "by_name_and_guild", return_value=None), patch.object(
            controller.ScheduledMessage, "createOrFail", return_value=self.record
        ) as create:
            await controller.create(Mock(), 10, payload())
        self.assertIs(create.call_args.kwargs["guild"], self.guild)
        self.assertEqual(create.call_args.kwargs["message"], "Hello\nworld")

    async def test_updates_schedule_preserving_last_send_and_attachment(self):
        self.record.attachment_path = "local://scheduled_messages/old"
        with patch.object(controller.ScheduledMessage, "whereFirst", return_value=self.record), patch.object(
            controller.ScheduledMessage, "by_name_and_guild", return_value=self.record
        ):
            result = await controller.update(Mock(), 10, 7, payload(time="19:00", message=""))
        self.assertEqual(result["time"], "19:00")
        self.assertEqual(self.record.last_sent_date, "2026-10-25")
        self.assertEqual(self.record.attachment_path,
                         "local://scheduled_messages/old")

    async def test_rejects_duplicate_names_and_foreign_channels(self):
        with patch.object(controller.ScheduledMessage, "by_name_and_guild", return_value=self.record), self.assertRaises(HTTPException) as error:
            await controller.create(Mock(), 10, payload())
        self.assertEqual(error.exception.status_code, 409)
        with self.assertRaises(HTTPException) as error:
            await controller.create(Mock(), 10, payload(channel_id="999"))
        self.assertEqual(error.exception.status_code, 404)

    async def test_channel_permissions_are_checked(self):
        self.permissions.send_messages = False
        with self.assertRaises(HTTPException) as error:
            await controller.create(Mock(), 10, payload())
        self.assertEqual(error.exception.status_code, 422)

    async def test_other_guild_message_is_inaccessible(self):
        with patch.object(controller.ScheduledMessage, "whereFirst", return_value=None) as query, self.assertRaises(HTTPException) as error:
            await controller.update(Mock(), 10, 7, payload())
        query.assert_called_once_with(id=7, guild=self.guild)
        self.assertEqual(error.exception.status_code, 404)

    async def test_delete_removes_schedule(self):
        with patch.object(controller.ScheduledMessage, "whereFirst", return_value=self.record):
            await controller.delete(Mock(), 10, 7)
        self.record.delete.assert_called_once_with()

    async def test_upload_stores_private_attachment_with_safe_filename(self):
        form = FormData({"attachment": UploadFile(
            BytesIO(b"file content"), filename="../../report.pdf")})
        with TemporaryDirectory() as directory, patch.object(controller, "ATTACHMENTS", Path(directory)), patch.object(
            controller.ScheduledMessage, "whereFirst", return_value=self.record
        ), patch.object(controller, "image_upload_form", new_callable=AsyncMock, return_value=form):
            result = await controller.upload_attachment(Mock(), 10, 7)
            self.assertEqual(result["attachment_name"], "report.pdf")
            self.assertTrue(result["has_attachment"])
            self.assertEqual(next(Path(directory).iterdir()
                                  ).read_bytes(), b"file content")
            self.assertNotIn("attachment_path", result)
        self.record.saveOrFail.assert_called_once_with()

    async def test_upload_database_failure_cleans_new_file(self):
        self.record.saveOrFail.side_effect = RuntimeError("database")
        form = FormData({"attachment": UploadFile(
            BytesIO(b"file content"), filename="report.pdf")})
        with TemporaryDirectory() as directory, patch.object(controller, "ATTACHMENTS", Path(directory)), patch.object(
            controller.ScheduledMessage, "whereFirst", return_value=self.record
        ), patch.object(controller, "image_upload_form", new_callable=AsyncMock, return_value=form):
            with self.assertRaises(RuntimeError):
                await controller.upload_attachment(Mock(), 10, 7)
            self.assertEqual(list(Path(directory).iterdir()), [])

    async def test_cannot_remove_only_content(self):
        self.record.message = ""
        with patch.object(controller.ScheduledMessage, "whereFirst", return_value=self.record), self.assertRaises(HTTPException) as error:
            await controller.remove_attachment(Mock(), 10, 7)
        self.assertEqual(error.exception.status_code, 422)

    async def test_every_action_requires_admin(self):
        self.context.side_effect = HTTPException(403)
        for method, args in ((controller.index, (Mock(), 10)), (controller.create, (Mock(), 10, payload())),
                             (controller.update, (Mock(), 10, 7, payload())
                              ), (controller.delete, (Mock(), 10, 7)),
                             (controller.upload_attachment, (Mock(), 10, 7)), (controller.remove_attachment, (Mock(), 10, 7))):
            with self.subTest(method=method.__name__), self.assertRaises(HTTPException):
                await method(*args)


class TestAutomaticMessageValidation(unittest.TestCase):
    def test_invalid_schedule_content_and_extra_fields(self):
        for changes in ({"name": " "}, {"channel_id": "bad"}, {"day": "never"}, {"time": "25:00"},
                        {"time": "9:00"}, {"timezone": "Not/AZone"}, {"message": "x" * 2001}, {"guild_id": 11}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                payload(**changes)

    def test_discord_command_removed(self):
        self.assertFalse(hasattr(AdminCommands, "automatic_message"))
