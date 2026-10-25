from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError
import discord

from cogs.barman.reaction_role import ReactionRole
from libs.utils.role_utils import RoleUtils
from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "guild_roles_controller", "http/controllers/guild_roles_controller.py")


class DiscordRole:
    def __init__(self, id=100, position=2, name="Adventurer", managed=False, default=False):
        self.id, self.position, self.name = id, position, name
        self.managed, self.default = managed, default
        self.color = "#ffcc77"
        self.permissions = SimpleNamespace(
            administrator=False, manage_roles=False, manage_guild=False)

    def is_default(self):
        return self.default

    def __ge__(self, other):
        return self.position >= other.position


def level_rule(**attributes):
    return controller.RoleWrite(discord_id="100", mode="level", level=5, **attributes)


def reaction_rule():
    return controller.RoleWrite(discord_id="100", mode="reaction", emoji="🎮", message_discord_id="123456789012345678")


def record(level=5):
    return SimpleNamespace(id=7, discord_id="100", level=level, emoji=None if level else "🎮",
                           message_discord_id=None if level else "123456789012345678", saveOrFail=Mock(), delete=Mock())


class TestRoleManagement(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.role = DiscordRole()
        self.guild = SimpleNamespace(id=10)
        self.actor = SimpleNamespace(id=42, top_role=DiscordRole(
            position=9), guild_permissions=SimpleNamespace(administrator=True))
        self.discord_guild = SimpleNamespace(owner_id=1, me=SimpleNamespace(
            guild_permissions=SimpleNamespace(manage_roles=True), top_role=DiscordRole(position=10)))
        context = patch.object(controller, "role_context", new_callable=AsyncMock,
                               return_value=(self.guild, self.discord_guild, [self.role], self.actor))
        self.context = context.start()
        self.addCleanup(context.stop)
        synchronizer = patch.object(RoleUtils, "update_all_user_role", new_callable=AsyncMock,
                                    return_value={"updated": 3, "failed": 0, "skipped": 0})
        self.synchronize = synchronizer.start()
        self.addCleanup(synchronizer.stop)

    async def test_list_is_guild_scoped_and_marks_unavailable_roles(self):
        with patch.object(controller.Role, "where", return_value=[record()]) as query:
            result = await controller.index(Mock(), 10)
        query.assert_called_once_with(guild=self.guild)
        self.assertEqual(result["rules"][0]["name"], "Adventurer")
        self.assertIsNone(result["roles"][0]["unavailable"])

    async def test_creates_level_rule_and_synchronizes(self):
        def create(**attributes):
            return SimpleNamespace(id=7, **attributes)
        with patch.object(controller.Role, "whereFirst", return_value=None), patch.object(
            controller.Role, "createOrFail", side_effect=create
        ) as save:
            result = await controller.create(Mock(), 10, level_rule())
        self.assertIs(save.call_args.kwargs["guild"], self.guild)
        self.assertEqual(result["rule"]["level"], 5)
        self.synchronize.assert_awaited_once_with(self.discord_guild)

    async def test_creates_reaction_rule_without_level_sync(self):
        with patch.object(controller.Role, "whereFirst", return_value=None), patch.object(
            controller.Role, "createOrFail", side_effect=lambda **attributes: SimpleNamespace(id=7, **attributes)
        ):
            result = await controller.create(Mock(), 10, reaction_rule())
        self.assertEqual(result["rule"]["emoji"], "🎮")
        self.assertIsNone(result["rule"]["level"])
        self.synchronize.assert_not_awaited()

    async def test_rejects_duplicate_role_and_level(self):
        for results, key in (([record()], "duplicateRole"), ([None, record()], "duplicateLevel")):
            with self.subTest(key=key), patch.object(controller.Role, "whereFirst", side_effect=results), patch.object(
                controller.Role, "createOrFail"
            ) as save, self.assertRaises(HTTPException) as error:
                await controller.create(Mock(), 10, level_rule())
            self.assertEqual(error.exception.status_code, 409)
            self.assertTrue(error.exception.detail.endswith(key))
            save.assert_not_called()

    async def test_role_must_exist_in_current_discord_guild(self):
        with self.assertRaises(HTTPException) as error:
            await controller.create(Mock(), 10, controller.RoleWrite(discord_id="999", mode="level", level=1))
        self.assertEqual(error.exception.status_code, 404)

    async def test_changing_level_rule_to_reaction_cleans_up_old_assignments(self):
        old = record()
        with patch.object(controller.Role, "whereFirst", side_effect=[old, None]):
            result = await controller.update(Mock(), 10, 7, reaction_rule())
        self.assertIsNone(old.level)
        self.assertEqual(old.emoji, "🎮")
        old.saveOrFail.assert_called_once_with()
        self.synchronize.assert_awaited_once_with(
            self.discord_guild, removed_roles=[self.role])
        self.assertEqual(result["rule"]["mode"], "reaction")

    async def test_removing_level_rule_removes_configuration_not_discord_role(self):
        old = record()
        with patch.object(controller.Role, "whereFirst", return_value=old) as lookup:
            await controller.delete(Mock(), 10, 7)
        lookup.assert_called_once_with(id=7, guild=self.guild)
        old.delete.assert_called_once_with()
        self.synchronize.assert_awaited_once_with(
            self.discord_guild, removed_roles=[self.role])

    async def test_removing_reaction_rule_preserves_existing_assignments(self):
        with patch.object(controller.Role, "whereFirst", return_value=record(level=None)):
            await controller.delete(Mock(), 10, 7)
        self.synchronize.assert_not_awaited()

    async def test_other_guild_rule_cannot_be_updated_or_removed(self):
        with patch.object(controller.Role, "whereFirst", return_value=None) as lookup:
            for method, arguments in ((controller.update, (Mock(), 10, 7, level_rule())), (controller.delete, (Mock(), 10, 7))):
                with self.assertRaises(HTTPException) as error:
                    await method(*arguments)
                self.assertEqual(error.exception.status_code, 404)
                self.assertEqual(lookup.call_args.kwargs, {
                                 "id": 7, "guild": self.guild})

    async def test_all_routes_require_admin_context(self):
        self.context.side_effect = HTTPException(403)
        for method, arguments in ((controller.index, (Mock(), 10)), (controller.create, (Mock(), 10, level_rule())),
                                  (controller.update, (Mock(), 10, 7, level_rule())
                                   ), (controller.delete, (Mock(), 10, 7)),
                                  (controller.sync, (Mock(), 10))):
            with self.subTest(method=method.__name__), self.assertRaises(HTTPException):
                await method(*arguments)
        self.synchronize.assert_not_awaited()


class TestRoleValidation(unittest.TestCase):
    def test_invalid_or_incomplete_rules_are_rejected(self):
        for attributes in ({"discord_id": "abc", "mode": "level", "level": 1},
                           {"discord_id": "100", "mode": "level"},
                           {"discord_id": "100", "mode": "level", "level": 0},
                           {"discord_id": "100", "mode": "level", "level": True},
                           {"discord_id": "100", "mode": "reaction", "emoji": "🎮"},
                           {"discord_id": "100", "mode": "reaction",
                               "emoji": "🎮", "message_discord_id": "bad"},
                           {"discord_id": "100", "mode": "level", "level": 1, "guild_id": 11}):
            with self.subTest(attributes=attributes), self.assertRaises(ValidationError):
                controller.RoleWrite(**attributes)

    def test_inactive_mode_fields_are_cleared(self):
        rule = level_rule(emoji="🎮", message_discord_id="123")
        self.assertIsNone(rule.emoji)
        self.assertIsNone(rule.message_discord_id)

    def test_permissions_hierarchy_and_privileged_roles_are_blocked(self):
        actor = SimpleNamespace(id=42, top_role=DiscordRole(position=8))
        guild = SimpleNamespace(owner_id=1, me=SimpleNamespace(
            guild_permissions=SimpleNamespace(manage_roles=True), top_role=DiscordRole(position=10)))
        cases = [(DiscordRole(default=True), "defaultRole"), (DiscordRole(managed=True), "managedRole"),
                 (DiscordRole(position=10), "botHierarchy"), (DiscordRole(position=8), "actorHierarchy")]
        for role, expected in cases:
            self.assertTrue(controller.role_unavailable(
                role, guild, actor).endswith(expected))
        privileged = DiscordRole()
        privileged.permissions.administrator = True
        self.assertTrue(controller.role_unavailable(
            privileged, guild, actor).endswith("privilegedRole"))
        guild.me.guild_permissions.manage_roles = False
        self.assertTrue(controller.role_unavailable(
            DiscordRole(), guild, actor).endswith("botPermission"))

    def test_guild_owner_bypasses_own_hierarchy_but_not_bot_hierarchy(self):
        actor = SimpleNamespace(id=1, top_role=DiscordRole(position=2))
        guild = SimpleNamespace(owner_id=1, me=SimpleNamespace(
            guild_permissions=SimpleNamespace(manage_roles=True), top_role=DiscordRole(position=10)))
        self.assertIsNone(controller.role_unavailable(
            DiscordRole(position=8), guild, actor))
        self.assertTrue(controller.role_unavailable(DiscordRole(
            position=10), guild, actor).endswith("botHierarchy"))


class TestRoleContext(unittest.IsolatedAsyncioTestCase):
    async def test_refreshes_discord_roles_and_rechecks_actor_permission(self):
        actor = SimpleNamespace(
            guild_permissions=SimpleNamespace(administrator=False))
        discord_guild = SimpleNamespace(fetch_roles=AsyncMock(
            return_value=[]), fetch_member=AsyncMock(return_value=actor))
        guild = SimpleNamespace(get_guild=lambda: discord_guild)
        with patch.object(controller.HTTPUtils, "get_guild_admin_from_session", new_callable=AsyncMock, return_value=guild), patch.object(
            controller.HTTPUtils, "get_user_from_session", return_value=SimpleNamespace(discord_id="42")
        ), self.assertRaises(HTTPException) as error:
            await controller.role_context(Mock(), 10)
        self.assertEqual(error.exception.status_code, 403)
        discord_guild.fetch_roles.assert_awaited_once_with()
        discord_guild.fetch_member.assert_awaited_once_with(42)


class TestAutomaticRoleAssignment(unittest.IsolatedAsyncioTestCase):
    async def test_highest_eligible_role_is_selected_without_querying_every_level(self):
        roles = [DiscordRole(id=100), DiscordRole(id=200), DiscordRole(id=300)]
        db_roles = [SimpleNamespace(level=1, discord_id="100"), SimpleNamespace(
            level=5, discord_id="200"), SimpleNamespace(level=10, discord_id="300")]
        guild = SimpleNamespace(id=10, roles=roles)
        member = SimpleNamespace(guild=guild, roles=[], add_roles=AsyncMock())
        database_guild = SimpleNamespace(roles=Mock())
        database_guild.roles.whereNotNull.return_value = db_roles
        with patch("libs.utils.role_utils.Guild.from_discord_id", return_value=database_guild):
            await RoleUtils.add_role(member, SimpleNamespace(level=6, has_accepted_rules=True))
        member.add_roles.assert_awaited_once_with(roles[1])
        database_guild.roles.whereNotNull.assert_called_once_with("level")

    async def test_rules_must_be_accepted_before_level_assignment(self):
        member = SimpleNamespace(add_roles=AsyncMock())
        await RoleUtils.add_role(member, SimpleNamespace(level=99, has_accepted_rules=False))
        member.add_roles.assert_not_awaited()

    async def test_sync_keeps_correct_role_and_preserves_unrelated_roles(self):
        low, correct, unrelated = DiscordRole(
            id=100), DiscordRole(id=200), DiscordRole(id=999)
        rows = [SimpleNamespace(level=1, discord_id="100"),
                SimpleNamespace(level=5, discord_id="200")]
        guild = SimpleNamespace(id=10, roles=[low, correct, unrelated])
        member = SimpleNamespace(guild=guild, roles=[
                                 low, correct, unrelated], add_roles=AsyncMock(), remove_roles=AsyncMock())
        database_guild = SimpleNamespace(roles=Mock())
        database_guild.roles.whereNotNull.return_value = rows
        with patch("libs.utils.role_utils.Guild.from_discord_id", return_value=database_guild):
            await RoleUtils.update_role(member, SimpleNamespace(level=6, has_accepted_rules=True))
        member.remove_roles.assert_awaited_once_with(low)
        member.add_roles.assert_not_awaited()

    async def test_synchronization_reports_failures_and_cleans_removed_level_roles(self):
        old_role = DiscordRole()
        first = SimpleNamespace(
            id=1, roles=[old_role], remove_roles=AsyncMock())
        second = SimpleNamespace(id=2, roles=[], remove_roles=AsyncMock())
        guild = SimpleNamespace(id=10, get_member=lambda id: {
                                1: first, 2: second}.get(id))
        rows = [SimpleNamespace(user=SimpleNamespace(
            discord_id=str(id))) for id in (1, 2, 3)]
        with patch("libs.utils.role_utils.Guild.from_discord_id", return_value=SimpleNamespace(guildusers=rows)), patch.object(
            RoleUtils, "update_role", new_callable=AsyncMock, side_effect=[None, RuntimeError("permissions")]
        ), patch("libs.utils.role_utils.Log.warning"):
            result = await RoleUtils.update_all_user_role(guild, removed_roles=[old_role])
        self.assertEqual(result, {"updated": 1, "failed": 1, "skipped": 1})
        first.remove_roles.assert_awaited_once_with(old_role)

    async def test_reaction_rules_work_without_accepted_rules_configuration(self):
        rule = record(level=None)
        guild = SimpleNamespace(
            accepted_rules_message_id=None, accepted_rules_emoji=None, roles=Mock())
        guild.roles.whereNull.return_value = [rule]
        cog = ReactionRole(Mock())
        event = SimpleNamespace(guild_id=10)
        with patch("cogs.barman.reaction_role.Guild.from_discord_id", return_value=guild), patch.object(
            cog, "add_role_with_reaction", new_callable=AsyncMock
        ) as add:
            await cog.on_raw_reaction_add(event)
        add.assert_awaited_once_with(event, int(
            rule.message_discord_id), rule.emoji, 100, "emoji_to_role")


class TestReactionEmoji(unittest.TestCase):
    def test_unicode_custom_mentions_and_legacy_custom_names(self):
        self.assertTrue(RoleUtils.emoji_matches(
            discord.PartialEmoji(name="🎮"), "🎮"))
        self.assertTrue(RoleUtils.emoji_matches(discord.PartialEmoji(
            name="gaming", id=123456789012345678), "<:gaming:123456789012345678>"))
        self.assertTrue(RoleUtils.emoji_matches(discord.PartialEmoji(
            name="gaming", id=123456789012345678), "gaming"))
        self.assertFalse(RoleUtils.emoji_matches(discord.PartialEmoji(
            name="gaming", id=456789012345678901), "<:gaming:123456789012345678>"))
        self.assertFalse(RoleUtils.emoji_matches(
            discord.PartialEmoji(name="🎮"), None))
