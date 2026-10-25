import json
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
from fastapi import HTTPException

from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "dashboard_controller", "http/controllers/dashboard_controller.py")


def member(id=42, name="Alice", **voice_flags):
    voice = {"mute": False, "self_mute": False, "deaf": False, "self_deaf": False,
             "self_stream": False, "self_video": False, **voice_flags}
    return SimpleNamespace(id=id, display_name=name, name=name.lower(), bot=False,
                           display_avatar=SimpleNamespace(
                               url="https://example.com/avatar.png"),
                           voice=SimpleNamespace(**voice))


def score(id=42, level=2, xp=100, monthly=200):
    return SimpleNamespace(user=SimpleNamespace(discord_id=str(id)), level=level, point=xp, monthly_point=monthly)


def channel(id, name, members, viewer=True, bot=True, position=0):
    return SimpleNamespace(id=id, name=name, members=members, position=position,
                           category=SimpleNamespace(name="The tavern"),
                           permissions_for=lambda actor: SimpleNamespace(view_channel=bot if actor.id == 0 else viewer))


class TestDashboard(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.alice, self.bob = member(), member(
            43, "Bob", self_mute=True, self_stream=True)
        self.guild = SimpleNamespace(id=10, get_monthly_top_users=Mock(return_value=[score(43, monthly=500), score()]),
                                     get_top_users=Mock(return_value=[score(42, level=5, xp=999), score(43)]))
        self.discord_guild = SimpleNamespace(name="Test guild", icon=None, me=SimpleNamespace(id=0),
                                             voice_channels=[channel(100, "General", [self.bob, self.alice])], stage_channels=[],
                                             get_member=lambda id: {42: self.alice, 43: self.bob}.get(id))
        context = patch.object(controller, "dashboard_context", new_callable=AsyncMock,
                               return_value=(self.guild, self.discord_guild, self.alice))
        self.context = context.start()
        self.addCleanup(context.stop)

    async def test_dashboard_shows_voice_members_and_both_rankings(self):
        result = await controller.show(Mock(), 10)
        self.assertEqual(result["guild"]["name"], "Test guild")
        self.assertEqual(result["voice_member_count"], 2)
        self.assertEqual(result["active_voice_channel_count"], 1)
        self.assertEqual([person["display_name"]
                         for person in result["voice_channels"][0]["members"]], ["Alice", "Bob"])
        self.assertEqual(result["monthly_top"][0]["display_name"], "Bob")
        self.assertEqual(result["monthly_top"][0]["monthly_xp"], 500)
        self.assertEqual(result["level_top"][0]["level"], 5)
        self.assertEqual(result["level_top"][0]["xp"], 999)
        self.guild.get_monthly_top_users.assert_called_once_with()
        self.guild.get_top_users.assert_called_once_with()

    async def test_private_channels_names_members_and_counts_are_not_exposed(self):
        self.discord_guild.voice_channels += [
            channel(200, "Secret staff room", [
                    member(99, "Secret participant")], viewer=False),
            channel(300, "Bot cannot see this", [
                    member(98, "Another secret")], bot=False),
        ]
        result = await controller.show(Mock(), 10)
        self.assertEqual(len(result["voice_channels"]), 1)
        self.assertEqual(result["voice_member_count"], 2)
        serialized = json.dumps(result)
        self.assertNotIn("Secret staff room", serialized)
        self.assertNotIn("Secret participant", serialized)
        self.assertNotIn("Bot cannot see this", serialized)
        self.assertNotIn("Another secret", serialized)

    async def test_includes_empty_channels_and_stage_channels(self):
        self.discord_guild.voice_channels += [
            channel(200, "Empty", [], position=2)]
        self.discord_guild.stage_channels = [
            channel(300, "Stage", [self.alice], position=1)]
        result = await controller.show(Mock(), 10)
        self.assertEqual([entry["name"] for entry in result["voice_channels"]], [
                         "General", "Stage", "Empty"])
        self.assertEqual(result["voice_channels"][1]["kind"], "stage")
        self.assertEqual(result["voice_channels"][2]["members"], [])
        self.assertEqual(result["active_voice_channel_count"], 2)

    async def test_voice_state_indicators(self):
        result = await controller.show(Mock(), 10)
        bob = result["voice_channels"][0]["members"][1]
        self.assertTrue(bob["muted"])
        self.assertTrue(bob["streaming"])
        self.assertFalse(bob["deafened"])
        self.assertFalse(bob["video"])

    async def test_missing_voice_state_does_not_break_dashboard(self):
        self.alice.voice = None
        result = await controller.show(Mock(), 10)
        self.assertFalse(result["voice_channels"][0]["members"][0]["muted"])

    async def test_no_activity_has_clean_empty_states(self):
        self.discord_guild.voice_channels = []
        self.guild.get_top_users.return_value = []
        self.guild.get_monthly_top_users.return_value = []
        result = await controller.show(Mock(), 10)
        self.assertEqual(result["voice_channels"], [])
        self.assertEqual(result["voice_member_count"], 0)
        self.assertEqual(result["monthly_top"], [])
        self.assertEqual(result["level_top"], [])

    async def test_access_denied_does_not_read_any_scores(self):
        self.context.side_effect = HTTPException(403)
        with self.assertRaises(HTTPException):
            await controller.show(Mock(), 10)
        self.guild.get_top_users.assert_not_called()
        self.guild.get_monthly_top_users.assert_not_called()


class TestDashboardRankings(unittest.TestCase):
    def test_missing_discord_profile_falls_back_to_id_and_default_avatar(self):
        result = controller.leaderboard(
            [score(99)], SimpleNamespace(get_member=lambda id: None))[0]
        self.assertEqual(result["display_name"], "99")
        self.assertFalse(result["in_guild"])
        self.assertEqual(result["avatar_url"],
                         "https://cdn.discordapp.com/embed/avatars/0.png")

    def test_ranking_is_capped_at_ten_and_preserves_database_order(self):
        result = controller.leaderboard([score(id) for id in range(
            12)], SimpleNamespace(get_member=lambda id: None))
        self.assertEqual(len(result), 10)
        self.assertEqual([entry["discord_id"]
                         for entry in result], [str(id) for id in range(10)])
        self.assertEqual([entry["rank"]
                         for entry in result], list(range(1, 11)))

    def test_xp_threshold_caps_at_level_fifteen(self):
        result = controller.leaderboard(
            [score(level=20, xp=1500)], SimpleNamespace(get_member=lambda id: member()))[0]
        self.assertEqual(result["xp_required"], 3000)
        self.assertEqual(result["progress"], 0.5)


class TestDashboardAccess(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.viewer = member()
        self.viewer.guild_permissions = SimpleNamespace(administrator=False)
        self.discord_guild = SimpleNamespace(
            me=member(0, "Bot"), fetch_member=AsyncMock(return_value=self.viewer))
        self.guild = SimpleNamespace(
            id=10, get_guild=Mock(return_value=self.discord_guild))

    async def context(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session", return_value=SimpleNamespace(discord_id="42")), patch.object(
            controller.Guild, "find", return_value=self.guild
        ), patch.object(controller.ApplicationModel, "bot", Mock(is_ready=Mock(return_value=True)), create=True):
            return await controller.dashboard_context(Mock(), 10)

    async def test_normal_guild_members_do_not_need_admin_permission(self):
        guild, _, viewer = await self.context()
        self.assertIs(guild, self.guild)
        self.assertIs(viewer, self.viewer)
        self.assertFalse(viewer.guild_permissions.administrator)
        self.discord_guild.fetch_member.assert_awaited_once_with(42)

    async def test_departed_members_cannot_view_guild_data(self):
        self.discord_guild.fetch_member.side_effect = discord.NotFound(
            SimpleNamespace(status=404, reason="Not found"), "Not found")
        with self.assertRaises(HTTPException) as error:
            await self.context()
        self.assertEqual(error.exception.status_code, 403)

    async def test_requires_login_before_looking_up_guild(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session", side_effect=HTTPException(401)), patch.object(
            controller.Guild, "find"
        ) as lookup, self.assertRaises(HTTPException):
            await controller.dashboard_context(Mock(), 10)
        lookup.assert_not_called()

    async def test_missing_guild_returns_404(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session"), patch.object(
            controller.Guild, "find", return_value=None
        ), self.assertRaises(HTTPException) as error:
            await controller.dashboard_context(Mock(), 10)
        self.assertEqual(error.exception.status_code, 404)

    async def test_unready_bot_fails_closed(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session"), patch.object(
            controller.Guild, "find", return_value=self.guild
        ), patch.object(controller.ApplicationModel, "bot", None, create=True), self.assertRaises(HTTPException) as error:
            await controller.dashboard_context(Mock(), 10)
        self.assertEqual(error.exception.status_code, 503)

    async def test_inaccessible_guild_fails_closed(self):
        self.guild.get_guild.return_value = None
        with self.assertRaises(HTTPException) as error:
            await self.context()
        self.assertEqual(error.exception.status_code, 403)
