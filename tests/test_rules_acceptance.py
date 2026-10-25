from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
from fastapi import HTTPException
from pydantic import ValidationError

from cogs.barman.admin_commands import AdminCommands
from cogs.barman.reaction_role import ReactionRole
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "guild_rules_acceptance_controller", "http/controllers/guild_rules_acceptance_controller.py")
GUILD_ID = "123456789012345678"
CHANNEL_ID = "234567890123456789"
MESSAGE_ID = "345678901234567890"
MESSAGE_LINK = f"https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}/{MESSAGE_ID}"


class TestRulesAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.channel = SimpleNamespace(
            fetch_message=AsyncMock(return_value=Mock()))
        self.discord_guild = SimpleNamespace(get_channel=Mock(
            return_value=self.channel), get_thread=Mock(return_value=None))
        self.guild = SimpleNamespace(id=10, discord_id=GUILD_ID, accepted_rules_message_id=MESSAGE_ID,
                                     accepted_rules_emoji="✅", saveOrFail=Mock(), get_guild=Mock(return_value=self.discord_guild))
        authorization = patch.object(
            controller.HTTPUtils, "get_guild_admin_from_session", new_callable=AsyncMock, return_value=self.guild)
        self.authorize = authorization.start()
        self.addCleanup(authorization.stop)

    async def test_shows_existing_configuration_without_migration(self):
        result = await controller.show(Mock(), 10)
        self.assertEqual(
            result, {"message_discord_id": MESSAGE_ID, "emoji": "✅"})
        self.guild.saveOrFail.assert_not_called()

    async def test_updates_plain_id_using_existing_guild_fields(self):
        result = await controller.update(Mock(), 10, controller.RulesAcceptanceWrite(message=MESSAGE_ID, emoji="🎮"))
        self.assertEqual(self.guild.accepted_rules_message_id, MESSAGE_ID)
        self.assertEqual(self.guild.accepted_rules_emoji, "🎮")
        self.assertEqual(result["emoji"], "🎮")
        self.guild.saveOrFail.assert_called_once_with()
        self.channel.fetch_message.assert_not_awaited()

    async def test_message_link_is_checked_and_saved_as_id(self):
        result = await controller.update(Mock(), 10, controller.RulesAcceptanceWrite(message=MESSAGE_LINK, emoji="✅"))
        self.discord_guild.get_channel.assert_called_once_with(int(CHANNEL_ID))
        self.channel.fetch_message.assert_awaited_once_with(int(MESSAGE_ID))
        self.assertEqual(result["message_discord_id"], MESSAGE_ID)

    async def test_thread_message_links_are_supported(self):
        self.discord_guild.get_channel.return_value = None
        self.discord_guild.get_thread.return_value = self.channel
        await controller.update(Mock(), 10, controller.RulesAcceptanceWrite(message=MESSAGE_LINK, emoji="✅"))
        self.discord_guild.get_thread.assert_called_once_with(int(CHANNEL_ID))
        self.channel.fetch_message.assert_awaited_once_with(int(MESSAGE_ID))

    async def test_rejects_another_guild_link_without_saving_or_fetching(self):
        link = MESSAGE_LINK.replace(GUILD_ID, "999999999999999999")
        with self.assertRaises(HTTPException) as error:
            await controller.update(Mock(), 10, controller.RulesAcceptanceWrite(message=link, emoji="✅"))
        self.assertEqual(error.exception.status_code, 422)
        self.channel.fetch_message.assert_not_awaited()
        self.guild.saveOrFail.assert_not_called()

    async def test_missing_channel_is_rejected(self):
        self.discord_guild.get_channel.return_value = None
        with self.assertRaises(HTTPException) as error:
            await controller.update(Mock(), 10, controller.RulesAcceptanceWrite(message=MESSAGE_LINK, emoji="✅"))
        self.assertEqual(error.exception.status_code, 404)
        self.guild.saveOrFail.assert_not_called()

    async def test_missing_message_and_access_denial_do_not_overwrite_configuration(self):
        for exception, status in ((discord.NotFound, 404), (discord.Forbidden, 403), (discord.HTTPException, 503)):
            with self.subTest(status=status):
                self.channel.fetch_message.side_effect = exception(
                    SimpleNamespace(status=status, reason="Error"), "Error")
                with self.assertRaises(HTTPException) as error:
                    await controller.update(Mock(), 10, controller.RulesAcceptanceWrite(message=MESSAGE_LINK, emoji="🎮"))
                self.assertEqual(error.exception.status_code, status)
                self.assertEqual(self.guild.accepted_rules_emoji, "✅")
        self.guild.saveOrFail.assert_not_called()

    async def test_disable_clears_configuration_without_touching_members(self):
        result = await controller.disable(Mock(), 10)
        self.assertEqual(result, {"message_discord_id": None, "emoji": None})
        self.guild.saveOrFail.assert_called_once_with()

    async def test_every_action_requires_current_guild_administration(self):
        self.authorize.side_effect = HTTPException(403)
        for method, arguments in ((controller.show, (Mock(), 10)),
                                  (controller.update, (Mock(), 10, controller.RulesAcceptanceWrite(
                                      message=MESSAGE_ID, emoji="✅"))),
                                  (controller.disable, (Mock(), 10))):
            with self.subTest(method=method.__name__), self.assertRaises(HTTPException):
                await method(*arguments)
        self.guild.saveOrFail.assert_not_called()


class TestRulesAcceptanceValidation(unittest.TestCase):
    def test_invalid_ids_links_and_blank_emojis_are_rejected(self):
        for changes in ({"message": "123"}, {"message": MESSAGE_ID + "invalid"},
                        {"message": "https://example.com/message"}, {
                            "message": MESSAGE_LINK.replace("/channels/", "/other/")},
                        {"emoji": " "}, {"guild_id": 11}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                controller.RulesAcceptanceWrite(
                    **{"message": MESSAGE_ID, "emoji": "✅", **changes})

    def test_unicode_and_custom_emoji_are_supported(self):
        for emoji in ("✅", "<:approve:123456789012345678>", "approve"):
            self.assertEqual(controller.RulesAcceptanceWrite(
                message=MESSAGE_ID, emoji=emoji).emoji, emoji)

    def test_discord_command_has_been_removed(self):
        self.assertFalse(
            hasattr(AdminCommands, "manage_accepted_rules_message"))


class TestRulesAcceptanceReaction(unittest.IsolatedAsyncioTestCase):
    async def test_configured_reaction_accepts_rules_and_assigns_level_role(self):
        member = Mock()
        record = SimpleNamespace(has_accepted_rules=False, save=Mock())
        event = SimpleNamespace(message_id=int(MESSAGE_ID), emoji=discord.PartialEmoji(name="✅"),
                                user_id=42, guild_id=int(GUILD_ID), member=member)
        cog = ReactionRole(Mock())
        with patch("cogs.barman.reaction_role.GuildUser.from_user_discord_id_and_guild_discord_id", return_value=record), patch(
            "cogs.barman.reaction_role.RoleUtils.add_role", new_callable=AsyncMock
        ) as assign:
            await cog.add_role_with_reaction(event, int(MESSAGE_ID), "✅", 0, "accept_rules")
        self.assertTrue(record.has_accepted_rules)
        record.save.assert_called_once_with()
        assign.assert_awaited_once_with(member, record)
