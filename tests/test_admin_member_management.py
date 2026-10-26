from contextlib import ExitStack
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
from fastapi import HTTPException
from pydantic import ValidationError

from libs.databases.models.guild_user import GuildUser
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "member_admin_controller", "http/controllers/guild_admin_controller.py")


def discord_member(id=42, name="Alice"):
    return SimpleNamespace(id=id, name=name.lower(), display_name=name, bot=False,
                           display_avatar=SimpleNamespace(url="https://example.com/avatar.png"))


class TestMemberManagement(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.target = discord_member()
        self.discord_guild = SimpleNamespace(
            members=[self.target], fetch_member=AsyncMock(return_value=self.target))
        self.guild = SimpleNamespace(
            id=10, get_guild=Mock(return_value=self.discord_guild))
        self.authorize = self.stack.enter_context(patch.object(controller.HTTPUtils,
                                                               "get_guild_admin_from_session", new_callable=AsyncMock, return_value=self.guild))
        self.user = SimpleNamespace(id=5, discord_id="42")
        self.record = SimpleNamespace(level=2, point=125, smartpoint=75,
                                      monthly_point=555, saveOrFail=Mock())
        self.stack.enter_context(patch.object(
            controller.User, "whereFirst", return_value=self.user))
        self.lookup = self.stack.enter_context(patch.object(
            controller.GuildUser, "whereFirst", return_value=self.record))
        self.batch_lookup = self.stack.enter_context(patch.object(
            controller.GuildUser, "for_discord_ids", return_value={"42": self.record}))
        self.stack.enter_context(patch.object(
            controller.User, "from_discord_id", return_value=self.user))
        self.get_record = self.stack.enter_context(patch.object(
            controller.GuildUser, "from_user_and_guild", return_value=self.record))

    async def test_lists_current_guild_member_balances_and_xp(self):
        request = Mock()
        result = await controller.members(request, 10, search="", page=1, page_size=20)
        self.authorize.assert_awaited_once_with(request, 10)
        self.batch_lookup.assert_called_once_with(self.guild, [42])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["members"][0]["smartpoint"], 75)
        self.assertEqual(result["members"][0]["xp"], 125)
        self.assertEqual(result["members"][0]["xp_required"], 400)
        self.assertEqual(result["members"][0]["discord_id"], "42")

    async def test_search_and_pagination(self):
        self.discord_guild.members = [discord_member(
            1, "Alice"), discord_member(2, "Bob"), discord_member(3, "Bobby")]
        result = await controller.members(Mock(), 10, search="BO", page=2, page_size=1)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["members"][0]["display_name"], "Bobby")
        self.batch_lookup.assert_called_once_with(self.guild, [3])

    async def test_untracked_members_show_defaults_without_creating_database_records(self):
        self.batch_lookup.return_value = {}
        with patch.object(controller.User, "whereFirst", return_value=None):
            result = await controller.members(Mock(), 10, search="42", page=1, page_size=20)
        self.assertEqual(result["members"][0]["level"], 1)
        self.assertEqual(result["members"][0]["xp"], 0)
        self.assertEqual(result["members"][0]["smartpoint"], 20)
        self.get_record.assert_not_called()

    async def test_sets_exact_values_in_current_guild_and_preserves_monthly_xp(self):
        changes = controller.MemberUpdate(smartpoint=500, level=5, xp=999)
        result = await controller.update_member(Mock(), 10, 42, changes)
        self.discord_guild.fetch_member.assert_awaited_once_with(42)
        self.get_record.assert_called_once_with(self.user, self.guild)
        self.record.saveOrFail.assert_called_once_with()
        self.assertEqual(result["level"], 5)
        self.assertEqual(result["xp"], 999)
        self.assertEqual(result["smartpoint"], 500)
        self.assertEqual(self.record.monthly_point, 555)

    async def test_member_outside_guild_cannot_be_modified(self):
        self.discord_guild.fetch_member.side_effect = discord.NotFound(
            SimpleNamespace(status=404, reason="Not found"), "Not found")
        with self.assertRaises(HTTPException) as error:
            await controller.update_member(Mock(), 10, 42, controller.MemberUpdate(smartpoint=1, level=1, xp=0))
        self.assertEqual(error.exception.status_code, 404)
        self.get_record.assert_not_called()
        self.record.saveOrFail.assert_not_called()

    async def test_admin_permission_required_for_list_and_update(self):
        self.authorize.side_effect = HTTPException(403)
        with self.assertRaises(HTTPException):
            await controller.members(Mock(), 10, search="", page=1, page_size=20)
        with self.assertRaises(HTTPException):
            await controller.update_member(Mock(), 10, 42, controller.MemberUpdate(smartpoint=1, level=1, xp=0))
        self.lookup.assert_not_called()
        self.batch_lookup.assert_not_called()
        self.discord_guild.fetch_member.assert_not_awaited()
        self.record.saveOrFail.assert_not_called()

    async def test_missing_discord_guild_fails_closed(self):
        self.guild.get_guild.return_value = None
        with self.assertRaises(HTTPException) as error:
            await controller.members(Mock(), 10, search="", page=1, page_size=20)
        self.assertEqual(error.exception.status_code, 503)


class TestMemberValues(unittest.TestCase):
    def test_invalid_values_and_extra_privileges_are_rejected(self):
        for changes in ({"smartpoint": -1}, {"smartpoint": 2147483648}, {"level": 0},
                        {"level": 1000001}, {"xp": -1}, {"xp": 200}, {"xp": 1.5},
                        {"level": True}, {"smartpoint": "5"}, {"is_admin": True}, {"guild_id": 11}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                controller.MemberUpdate(
                    **{"smartpoint": 20, "level": 1, "xp": 0, **changes})

    def test_level_threshold_caps_at_fifteen(self):
        self.assertEqual(controller.MemberUpdate(
            smartpoint=0, level=20, xp=2999).xp, 2999)
        with self.assertRaises(ValidationError):
            controller.MemberUpdate(smartpoint=0, level=20, xp=3000)

    def test_valid_manual_progress_does_not_trigger_level_up_rewards(self):
        member = object.__new__(GuildUser)
        member._attributes = {"level": 1, "point": 0, "smartpoint": 20}
        member._modified_attributes = {}
        changes = controller.MemberUpdate(smartpoint=500, level=5, xp=999)
        member.level = changes.level
        member.point = changes.xp
        member.smartpoint = changes.smartpoint
        member.beforeSave()
        self.assertEqual(member.level, 5)
        self.assertEqual(member.point, 999)
        self.assertEqual(member.smartpoint, 500)


class TestWallpaperEditing(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.guild = SimpleNamespace(id=10)
        self.wallpaper = SimpleNamespace(id=7, name="Old name", price=20, level=0,
                                         url="https://example.com/original.png", saveOrFail=Mock())
        authorization = patch.object(
            controller.HTTPUtils, "get_guild_admin_from_session", new_callable=AsyncMock, return_value=self.guild)
        self.authorize = authorization.start()
        self.addCleanup(authorization.stop)

    async def test_updates_metadata_without_touching_image(self):
        with patch.object(controller.Wallpaper, "whereFirst", side_effect=[self.wallpaper, None]) as lookup:
            result = await controller.update_wallpaper(Mock(), 10, 7, controller.WallpaperCreate(name="New name", price=100, level=3))
        self.assertEqual(lookup.call_args_list[0].kwargs, {
                         "id": 7, "guild_id": 10})
        self.assertEqual(result["name"], "New name")
        self.assertEqual(result["price"], 100)
        self.assertEqual(result["level"], 3)
        self.assertEqual(result["url"], "https://example.com/original.png")
        self.wallpaper.saveOrFail.assert_called_once_with()

    async def test_can_keep_own_name_and_disable_unlock_options(self):
        with patch.object(controller.Wallpaper, "whereFirst", side_effect=[self.wallpaper, self.wallpaper]):
            result = await controller.update_wallpaper(Mock(), 10, 7, controller.WallpaperCreate(name="Old name", price=0, level=0))
        self.assertEqual(result["price"], 0)
        self.assertEqual(result["level"], 0)

    async def test_duplicate_name_is_rejected(self):
        with patch.object(controller.Wallpaper, "whereFirst", side_effect=[self.wallpaper, SimpleNamespace(id=8)]), self.assertRaises(HTTPException) as error:
            await controller.update_wallpaper(Mock(), 10, 7, controller.WallpaperCreate(name="Duplicate", price=1, level=0))
        self.assertEqual(error.exception.status_code, 409)
        self.wallpaper.saveOrFail.assert_not_called()

    async def test_other_guild_wallpaper_is_not_accessible(self):
        with patch.object(controller.Wallpaper, "whereFirst", return_value=None) as lookup, self.assertRaises(HTTPException) as error:
            await controller.update_wallpaper(Mock(), 10, 7, controller.WallpaperCreate(name="Name", price=1, level=0))
        self.assertEqual(error.exception.status_code, 404)
        lookup.assert_called_once_with(id=7, guild_id=10)

    async def test_editing_requires_admin_permission(self):
        self.authorize.side_effect = HTTPException(403)
        with patch.object(controller.Wallpaper, "whereFirst") as lookup, self.assertRaises(HTTPException):
            await controller.update_wallpaper(Mock(), 10, 7, controller.WallpaperCreate(name="Name", price=1, level=0))
        lookup.assert_not_called()
