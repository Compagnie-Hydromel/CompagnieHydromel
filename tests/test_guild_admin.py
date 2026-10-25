from contextlib import ExitStack, closing
import importlib
import sqlite3
from io import BytesIO
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.datastructures import FormData, UploadFile

from libs.databases.models.profile_layout import ProfileLayout
from libs.utils.http_utils import HTTPUtils
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "guild_admin_controller", "http/controllers/guild_admin_controller.py")


def layout_attributes():
    return {
        "name": "The adventurer", "profile_picture_x": 0, "profile_picture_y": 0,
        "name_x": 150, "name_y": 20, "username_x": 150, "username_y": 65,
        "level_x": 250, "level_y": 224, "badge_x": 150, "badge_y": 90,
        "level_bar_x": 0, "level_bar_y": 254,
    }


def wallpaper_form():
    return FormData({"name": "Forest", "price": "50", "level": "0",
                     "image": UploadFile(BytesIO(b"image"), filename="forest.png")})


class TestDiscordAdminSynchronization(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.guild = SimpleNamespace(id=10, discord_id="123")
        self.user = SimpleNamespace(id=1, discord_id="456")
        self.stored = SimpleNamespace(is_admin=False, saveOrFail=Mock())
        self.member = SimpleNamespace(
            guild_permissions=SimpleNamespace(administrator=True))
        self.discord_guild = Mock(
            fetch_member=AsyncMock(return_value=self.member))
        self.bot = Mock()
        self.bot.is_ready.return_value = True
        self.bot.get_guild.return_value = self.discord_guild
        self.stack.enter_context(
            patch("libs.utils.http_utils.ApplicationModel.bot", self.bot, create=True))
        self.stack.enter_context(patch(
            "libs.utils.http_utils.GuildUser.from_user_and_guild", return_value=self.stored))
        self.stack.enter_context(
            patch("libs.utils.http_utils.GuildUser.whereFirst", return_value=self.stored))
        self.stack.enter_context(
            patch("libs.utils.http_utils.Guild.find", return_value=self.guild))
        self.stack.enter_context(patch.object(
            HTTPUtils, "get_user_from_session", return_value=self.user))

    async def test_discord_administrator_checks_database_flag(self):
        guild = await HTTPUtils.get_guild_admin_from_session(Mock(), 10)
        self.assertIs(guild, self.guild)
        self.assertTrue(self.stored.is_admin)
        self.stored.saveOrFail.assert_called_once_with()
        self.discord_guild.fetch_member.assert_awaited_once_with(456)

    async def test_revoked_permission_unchecks_database_flag_and_denies_access(self):
        self.stored.is_admin = True
        self.member.guild_permissions.administrator = False
        with self.assertRaises(HTTPException) as error:
            await HTTPUtils.get_guild_admin_from_session(Mock(), 10)
        self.assertEqual(error.exception.status_code, 403)
        self.assertFalse(self.stored.is_admin)
        self.stored.saveOrFail.assert_called_once_with()

    async def test_normal_member_stays_non_admin(self):
        self.member.guild_permissions.administrator = False
        result = await HTTPUtils.sync_guild_admin(self.user, self.guild)
        self.assertIs(result, self.stored)
        self.assertFalse(result.is_admin)
        self.stored.saveOrFail.assert_not_called()

    async def test_unchanged_admin_flag_is_not_saved_again(self):
        self.stored.is_admin = True
        await HTTPUtils.sync_guild_admin(self.user, self.guild)
        self.stored.saveOrFail.assert_not_called()

    async def test_discord_unavailable_fails_closed(self):
        self.bot.is_ready.return_value = False
        with self.assertRaises(HTTPException) as error:
            await HTTPUtils.get_guild_admin_from_session(Mock(), 10)
        self.assertEqual(error.exception.status_code, 503)
        self.discord_guild.fetch_member.assert_not_awaited()

    async def test_missing_guild_fails_closed(self):
        self.bot.get_guild.return_value = None
        with self.assertRaises(HTTPException) as error:
            await HTTPUtils.get_guild_admin_from_session(Mock(), 10)
        self.assertEqual(error.exception.status_code, 403)

    async def test_departed_member_loses_admin_flag(self):
        self.stored.is_admin = True
        self.discord_guild.fetch_member.side_effect = discord.NotFound(
            SimpleNamespace(status=404, reason="Not found"), "Not found")
        with self.assertRaises(HTTPException) as error:
            await HTTPUtils.get_guild_admin_from_session(Mock(), 10)
        self.assertEqual(error.exception.status_code, 403)
        self.assertFalse(self.stored.is_admin)

    async def test_requires_login_before_checking_discord(self):
        with patch.object(HTTPUtils, "get_user_from_session", side_effect=HTTPException(401)), self.assertRaises(HTTPException) as error:
            await HTTPUtils.get_guild_admin_from_session(Mock(), 10)
        self.assertEqual(error.exception.status_code, 401)
        self.discord_guild.fetch_member.assert_not_awaited()


class TestGuildAdminCreation(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.guild = SimpleNamespace(id=10)
        self.authorize = patch.object(
            HTTPUtils, "get_guild_admin_from_session", new_callable=AsyncMock, return_value=self.guild)
        self.authorize.start()
        self.addCleanup(self.authorize.stop)

    async def test_creates_layout_in_authorized_guild(self):
        payload = controller.LayoutCreate(**layout_attributes())
        with patch.object(ProfileLayout, "whereFirst", return_value=None), patch.object(
            ProfileLayout, "createOrFail", return_value=Mock()
        ) as create, patch.object(controller, "layout_data", return_value={"id": 1}):
            self.assertEqual(await controller.create_layout(Mock(), 10, payload), {"id": 1})
        self.assertIs(create.call_args.kwargs["guild"], self.guild)
        self.assertEqual(create.call_args.kwargs["profil_picture_x"], 0)
        self.assertNotIn("profile_picture_x", create.call_args.kwargs)

    async def test_duplicate_layout_is_rejected(self):
        with patch.object(ProfileLayout, "whereFirst", return_value=Mock()), patch.object(
            ProfileLayout, "createOrFail"
        ) as create, self.assertRaises(HTTPException) as error:
            await controller.create_layout(Mock(), 10, controller.LayoutCreate(**layout_attributes()))
        self.assertEqual(error.exception.status_code, 409)
        create.assert_not_called()

    async def test_creates_wallpaper_in_authorized_guild(self):
        wallpaper = SimpleNamespace(
            id=1, name="Forest", url="local://wallpapers/10-" + "a" * 32 + ".png", price=50, level=0)
        with patch.object(controller.Wallpaper, "whereFirst", return_value=None), patch.object(
            controller.Wallpaper, "createOrFail", return_value=wallpaper
        ) as create, patch.object(controller, "wallpaper_form", new_callable=AsyncMock, return_value=wallpaper_form()), patch.object(
            controller.WallpaperUploads, "store", return_value=wallpaper.url
        ):
            result = await controller.create_wallpaper(Mock(), 10)
        self.assertEqual(result["price"], 50)
        self.assertTrue(result["url"].startswith("/api/wallpapers/"))
        self.assertIs(create.call_args.kwargs["guild"], self.guild)

    async def test_admin_catalog_queries_only_authorized_guild(self):
        self.guild.name = "Test guild"
        self.guild.wallpapers = []
        with patch.object(ProfileLayout, "where", return_value=[]) as layouts, patch.object(
            ProfileLayout, "default", return_value=Mock()
        ), patch.object(controller, "layout_data", return_value={}), patch.object(
            controller.Wallpaper, "default", return_value=SimpleNamespace(url="default.png")
        ):
            result = await controller.index(Mock(), 10)
        self.assertEqual(result["guild_name"], "Test guild")
        self.assertEqual(result["wallpapers"], [])
        layouts.assert_called_once_with(guild_id=10)

    async def test_duplicate_wallpaper_is_rejected(self):
        with patch.object(controller.Wallpaper, "whereFirst", return_value=Mock()), patch.object(
            controller.Wallpaper, "createOrFail"
        ) as create, patch.object(controller, "wallpaper_form", new_callable=AsyncMock, return_value=wallpaper_form()), self.assertRaises(HTTPException) as error:
            await controller.create_wallpaper(Mock(), 10)
        self.assertEqual(error.exception.status_code, 409)
        create.assert_not_called()

    async def test_unauthorized_user_cannot_create_assets(self):
        with patch.object(HTTPUtils, "get_guild_admin_from_session", new_callable=AsyncMock, side_effect=HTTPException(403)), patch.object(
            ProfileLayout, "createOrFail"
        ) as create_layout, patch.object(controller.Wallpaper, "createOrFail") as create_wallpaper:
            with self.assertRaises(HTTPException):
                await controller.create_layout(Mock(), 10, controller.LayoutCreate(**layout_attributes()))
            with self.assertRaises(HTTPException):
                await controller.create_wallpaper(Mock(), 10)
        create_layout.assert_not_called()
        create_wallpaper.assert_not_called()


class TestAdminValidationAndScoping(unittest.TestCase):
    def test_layout_coordinates_are_bounded_and_names_required(self):
        for changes in ({"name": " "}, {"profile_picture_x": 373}, {"name_y": -1}, {"guild_id": 11}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                controller.LayoutCreate(**{**layout_attributes(), **changes})

    def test_wallpaper_validation(self):
        for changes in ({"name": " "}, {"url": "https://example.com/a.png"},
                        {"price": -1}, {"level": -1}, {"guild_id": 11}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                controller.WallpaperCreate(**{
                    "name": "Forest", "price": 20, "level": 0, **changes})

    def test_only_shared_and_current_guild_layouts_are_available(self):
        shared, own, other = [SimpleNamespace(
            id=id, guild_id=guild_id) for id, guild_id in ((1, None), (2, 10), (3, 11))]
        with patch.object(ProfileLayout, "all", return_value=[shared, own, other]):
            self.assertEqual(
                ProfileLayout.available_for_guild(10), [shared, own])

    def test_layout_migration_and_rollback_preserve_legacy_layouts(self):
        migration = importlib.import_module(
            "libs.databases.migrations.20261025120000_scope_profile_layouts_to_guilds")
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.execute(
                "CREATE TABLE profilelayouts (id INTEGER PRIMARY KEY, name TEXT)")
            connection.execute(
                "INSERT INTO profilelayouts VALUES (1, 'Legacy')")
            executor = SimpleNamespace(
                commit=lambda sql: connection.execute(sql))
            with patch.object(migration, "executor_select", return_value=executor):
                instance = migration.ScopeProfileLayoutsToGuilds()
                instance.migrate()
                self.assertEqual(connection.execute(
                    "SELECT guild_id FROM profilelayouts").fetchone(), (None,))
                connection.execute(
                    "INSERT INTO profilelayouts VALUES (2, 'Guild layout', 10)")
                instance.rollback()
            self.assertEqual(connection.execute(
                "SELECT * FROM profilelayouts").fetchall(), [(1, "Legacy")])
