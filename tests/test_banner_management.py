from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from PIL import Image
from pydantic import ValidationError
from starlette.requests import Request

from cogs.barman.admin_commands import AdminCommands
from cogs.barman.banner_updater import BannerUpdater
from libs.storages.banner_uploads import BannerUploads
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "guild_banner_controller", "http/controllers/guild_banner_controller.py")
media = Utils.import_module_from_path(
    "banners_controller", "http/controllers/banners_controller.py")


def upload_request(content):
    body = (b'--banner\r\nContent-Disposition: form-data; name="image"; filename="../../unsafe.png"\r\n'
            b'Content-Type: image/png\r\n\r\n' + content + b'\r\n--banner--\r\n')

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request({"type": "http", "method": "POST", "headers": [
        (b"content-type", b"multipart/form-data; boundary=banner")
    ]}, receive)


def png_bytes():
    output = BytesIO()
    Image.new("RGB", (100, 100), "blue").save(output, format="PNG")
    return output.getvalue()


class TestBannerManagement(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.channel = SimpleNamespace(id=100, name="Tavern", members=[])
        self.discord_guild = SimpleNamespace(voice_channels=[self.channel], features=["BANNER"],
                                             me=SimpleNamespace(guild_permissions=SimpleNamespace(manage_guild=True)))
        self.guild = SimpleNamespace(
            id=10, banner_image="https://example.com/legacy.png", saveOrFail=Mock())
        context = patch.object(controller, "banner_context", new_callable=AsyncMock, return_value=(
            self.guild, self.discord_guild))
        self.context = context.start()
        self.addCleanup(context.stop)
        self.record = SimpleNamespace(
            id=1, discord_id="100", x=0, y=0, saveOrFail=Mock(), delete=Mock())
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "banners"
        directory = patch.object(BannerUploads, "DIRECTORY", self.root)
        directory.start()
        self.addCleanup(directory.stop)

    async def test_lists_existing_banner_and_guild_scoped_channels(self):
        with patch.object(controller.VoiceChannel, "where", return_value=[self.record]) as lookup:
            result = await controller.index(Mock(), 10)
        lookup.assert_called_once_with(guild=self.guild)
        self.assertEqual(result["image_url"], self.guild.banner_image)
        self.assertEqual(result["channels"][0]["name"], "Tavern")
        self.assertEqual(result["channels"][0]["x"], 0)
        self.assertTrue(result["can_update_banner"])

    async def test_creates_channel_at_zero_coordinates(self):
        with patch.object(controller.VoiceChannel, "whereFirst", return_value=None), patch.object(
            controller.VoiceChannel, "createOrFail", return_value=self.record
        ) as create:
            result = await controller.create_channel(Mock(), 10, controller.ChannelWrite(discord_id="100", x=0, y=0))
        self.assertEqual(result["x"], 0)
        create.assert_called_once_with(
            guild=self.guild, discord_id="100", x=0, y=0)

    async def test_channel_must_exist_in_current_guild(self):
        with patch.object(controller.VoiceChannel, "createOrFail") as create, self.assertRaises(HTTPException) as error:
            await controller.create_channel(Mock(), 10, controller.ChannelWrite(discord_id="999", x=0, y=0))
        self.assertEqual(error.exception.status_code, 404)
        create.assert_not_called()

    async def test_duplicate_channel_is_rejected(self):
        with patch.object(controller.VoiceChannel, "whereFirst", return_value=self.record), self.assertRaises(HTTPException) as error:
            await controller.create_channel(Mock(), 10, controller.ChannelWrite(discord_id="100", x=0, y=0))
        self.assertEqual(error.exception.status_code, 409)

    async def test_updates_position_only_in_current_guild(self):
        with patch.object(controller.VoiceChannel, "whereFirst", return_value=self.record) as lookup:
            result = await controller.update_channel(Mock(), 10, 1, controller.PositionWrite(x=50, y=100))
        lookup.assert_called_once_with(id=1, guild=self.guild)
        self.assertEqual((result["x"], result["y"]), (50, 100))
        self.record.saveOrFail.assert_called_once_with()

    async def test_other_guild_channel_cannot_be_updated_or_removed(self):
        with patch.object(controller.VoiceChannel, "whereFirst", return_value=None) as lookup:
            for method, arguments in ((controller.update_channel, (Mock(), 10, 1, controller.PositionWrite(x=0, y=0))),
                                      (controller.delete_channel, (Mock(), 10, 1))):
                with self.assertRaises(HTTPException) as error:
                    await method(*arguments)
                self.assertEqual(error.exception.status_code, 404)
                self.assertEqual(lookup.call_args.kwargs, {
                                 "id": 1, "guild": self.guild})

    async def test_removes_configuration_not_discord_channel(self):
        with patch.object(controller.VoiceChannel, "whereFirst", return_value=self.record):
            await controller.delete_channel(Mock(), 10, 1)
        self.record.delete.assert_called_once_with()

    async def test_real_image_upload_is_stored_for_web_and_bot(self):
        result = await controller.upload(upload_request(png_bytes()), 10)
        self.assertTrue(result["image_url"].startswith("/api/banners/10-"))
        self.assertTrue(self.guild.banner_image.startswith(
            "local://banners/10-"))
        self.guild.saveOrFail.assert_called_once_with()
        filename = result["image_url"].rsplit("/", 1)[1]
        with Image.open(BannerUploads.image_path(filename)) as image:
            self.assertEqual(image.size, (960, 540))
            self.assertEqual(image.format, "PNG")
        response = await media.image(filename)
        self.assertEqual(response.media_type, "image/png")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")

    async def test_database_failure_cleans_up_just_uploaded_image(self):
        self.guild.saveOrFail.side_effect = RuntimeError("database failed")
        with self.assertRaisesRegex(RuntimeError, "database failed"):
            await controller.upload(upload_request(png_bytes()), 10)
        self.assertEqual(list(self.root.iterdir()), [])

    async def test_invalid_image_is_rejected(self):
        with self.assertRaises(HTTPException) as error:
            await controller.upload(upload_request(b"not an image"), 10)
        self.assertEqual(error.exception.status_code, 422)
        self.guild.saveOrFail.assert_not_called()

    async def test_disable_leaves_channel_configuration_and_discord_banner_alone(self):
        result = await controller.disable(Mock(), 10)
        self.assertEqual(result, {"image_url": None})
        self.assertIsNone(self.guild.banner_image)
        self.guild.saveOrFail.assert_called_once_with()

    async def test_every_action_requires_guild_administration(self):
        self.context.side_effect = HTTPException(403)
        methods = ((controller.index, (Mock(), 10)), (controller.upload, (Mock(), 10)), (controller.disable, (Mock(), 10)),
                   (controller.create_channel, (Mock(), 10,
                    controller.ChannelWrite(discord_id="100", x=0, y=0))),
                   (controller.update_channel, (Mock(), 10,
                    1, controller.PositionWrite(x=0, y=0))),
                   (controller.delete_channel, (Mock(), 10, 1)))
        with patch.object(controller, "image_upload_form", new_callable=AsyncMock) as parse:
            for method, arguments in methods:
                with self.subTest(method=method.__name__), self.assertRaises(HTTPException):
                    await method(*arguments)
        parse.assert_not_awaited()
        self.guild.saveOrFail.assert_not_called()


class TestBannerValidation(unittest.TestCase):
    def test_invalid_coordinates_and_extra_guild_fields_are_rejected(self):
        for changes in ({"x": -1}, {"y": -1}, {"x": 16385}, {"x": 1.5}, {"x": True}, {"guild_id": 11}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                controller.ChannelWrite(
                    **{"discord_id": "100", "x": 0, "y": 0, **changes})

    def test_old_command_is_removed(self):
        self.assertFalse(
            hasattr(AdminCommands, "manage_banner_voice_channels"))

    def test_deleted_voice_channels_are_skipped_and_cache_is_guild_specific(self):
        bot = Mock()
        bot.get_guild.return_value = SimpleNamespace(channels=[])
        guild = SimpleNamespace(id=10, discord_id="123", banner_image="https://example.com/banner.png",
                                voicechannels=[SimpleNamespace(discord_id="999", x=0, y=0)])
        cog = BannerUpdater(bot)
        with patch("cogs.barman.banner_updater.BannerBarCreator", return_value=SimpleNamespace(file_path="result.png")) as render:
            result = cog._BannerUpdater__get_bar_image(guild)
        self.assertEqual(result, "result.png")
        self.assertEqual(render.call_args.args[0], "caches://banner_10.png")
        self.assertEqual(render.call_args.args[3], {999: []})
