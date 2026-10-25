from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "superadmin_users_controller", "http/controllers/superadmin_users_controller.py")


class TestSuperadminUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=7, discord_id="123456789012345678", is_superadmin=False,
                                    badges=[SimpleNamespace(id=1, name="Hero", url="https://example.com/badge.png")], guildusers=[])
        authorization = patch.object(
            controller.HTTPUtils, "get_superadmin_from_session", return_value=Mock())
        self.authorize = authorization.start()
        self.addCleanup(authorization.stop)
        bot = patch.object(controller.User, "bot", None, create=True)
        bot.start()
        self.addCleanup(bot.stop)

    async def test_details_include_badges_and_progress_for_each_recorded_guild(self):
        guild = SimpleNamespace(id=10, discord_id="234567890123456789")
        self.user.guildusers = [SimpleNamespace(guild=guild, level=20, point=1500, monthly_point=400,
                                                smartpoint=900, is_admin=True, has_accepted_rules=True)]
        with patch.object(controller.User, "find", return_value=self.user):
            result = await controller.show(Mock(), 7)
        self.assertEqual(result["badges"][0]["name"], "Hero")
        self.assertEqual(result["guilds"][0]["level"], 20)
        self.assertEqual(result["guilds"][0]["xp_required"], 3000)
        self.assertEqual(result["guilds"][0]["monthly_xp"], 400)
        self.assertEqual(result["guilds"][0]["smartpoint"], 900)
        self.assertTrue(result["guilds"][0]["is_admin"])
        self.assertFalse(result["guilds"][0]["cached_member"])

    async def test_live_cached_names_and_guild_icons_are_resolved(self):
        member = SimpleNamespace(
            display_name="Alice", name="alice", display_avatar=SimpleNamespace(url="avatar.png"))
        guild = SimpleNamespace(id=10, discord_id="234567890123456789")
        self.user.guildusers = [SimpleNamespace(guild=guild, level=1, point=0, monthly_point=0,
                                                smartpoint=20, is_admin=False, has_accepted_rules=False)]
        bot = SimpleNamespace(get_user=lambda id: member, get_guild=lambda id: SimpleNamespace(
            name="Tavern", icon=SimpleNamespace(url="icon.png"), get_member=lambda id: member))
        with patch.object(controller.User, "bot", bot), patch.object(controller.User, "find", return_value=self.user):
            result = await controller.show(Mock(), 7)
        self.assertEqual(result["display_name"], "Alice")
        self.assertEqual(result["guilds"][0]["name"], "Tavern")
        self.assertTrue(result["guilds"][0]["cached_member"])

    async def test_user_search_works_with_id_and_cached_name(self):
        bot = SimpleNamespace(get_user=lambda id: SimpleNamespace(
            display_name="Alice", name="alice", display_avatar=SimpleNamespace(url="avatar.png")))
        with patch.object(controller.User, "bot", bot), patch.object(controller.User, "all", return_value=[self.user]):
            for search in ("ALICE", "123456"):
                result = await controller.index(Mock(), search=search, page=1)
                self.assertEqual(result["total"], 1)
            self.assertEqual((await controller.index(Mock(), search="missing", page=1))["total"], 0)

    async def test_pagination_is_bounded(self):
        users = [SimpleNamespace(id=id, discord_id=str(
            123456789012345678 + id), is_superadmin=False) for id in range(25)]
        with patch.object(controller.User, "all", return_value=users):
            result = await controller.index(Mock(), search="", page=2)
        self.assertEqual(result["total"], 25)
        self.assertEqual(len(result["users"]), 5)

    async def test_missing_user_returns_404(self):
        with patch.object(controller.User, "find", return_value=None), self.assertRaises(HTTPException) as error:
            await controller.show(Mock(), 7)
        self.assertEqual(error.exception.status_code, 404)

    async def test_all_user_views_require_superadmin(self):
        self.authorize.side_effect = HTTPException(403)
        with patch.object(controller.User, "find") as lookup, patch.object(controller.User, "all") as listing:
            with self.assertRaises(HTTPException):
                await controller.show(Mock(), 7)
            with self.assertRaises(HTTPException):
                await controller.index(Mock(), search="", page=1)
        lookup.assert_not_called()
        listing.assert_not_called()
