import importlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from MIWOS.config import DBConfig
from MIWOS.db import migrate, rollback
from MIWOS.libs.sql.select import executor_select

from libs.databases.bootstrap import load_all_models
from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.profile_layout import ProfileLayout
from libs.databases.models.user import User


class TestMiwosIntegration(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        config = patch.dict(DBConfig._config, db_connector="sqlite",
                            db_database=str(
                                Path(directory.name) / "test.sqlite3"),
                            db_migration_dir="libs/databases/migrations", sql_log_file="")
        config.start()
        self.addCleanup(config.stop)
        self.executor = executor_select()
        self.addCleanup(self.executor.close)
        load_all_models()
        migrate()
        self.guild = Guild.createOrFail(discord_id="1000")
        self.other_guild = Guild.createOrFail(discord_id="2000")

    def create_member(self, discord_id, guild=None, **attributes):
        user = User.createOrFail(discord_id=str(discord_id))
        return GuildUser.createOrFail(user=user, guild=guild or self.guild, **attributes)

    def test_member_page_uses_two_queries_and_keeps_guild_balances_separate(self):
        for id in range(1, 21):
            record = self.create_member(id, smartpoint=100 + id)
            GuildUser.createOrFail(
                user_id=record.user_id, guild=self.other_guild, smartpoint=9999)
        self.create_member(21, guild=self.other_guild)
        User.createOrFail(discord_id="22")
        requested_ids = list(range(1, 24))
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            records = GuildUser.for_discord_ids(self.guild, requested_ids)
            self.assertEqual(len(records), 20)
            self.assertEqual(records["1"].smartpoint, 101)
            self.assertTrue(
                all(record.guild_id == self.guild.id for record in records.values()))
            self.assertEqual(execute.call_count, 2)
        self.assertEqual(len(User.all()), 22)
        self.assertEqual(len(GuildUser.all()), 41)

    def test_empty_member_page_never_queries_or_creates_records(self):
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            self.assertEqual(GuildUser.for_discord_ids(self.guild, []), {})
            execute.assert_not_called()
        self.assertEqual(GuildUser.for_discord_ids(self.guild, [404]), {})
        self.assertEqual(len(User.all()), 0)

    def test_each_ranking_fetches_ten_members_and_users_in_two_queries(self):
        for id in range(1, 16):
            self.create_member(
                id, level=id, monthly_point=id * 10, smartpoint=id * 100)
        self.create_member(100, guild=self.other_guild,
                           level=100, monthly_point=9999, smartpoint=99999)
        for ranking in (self.guild.get_monthly_top_users, self.guild.get_top_users, self.guild.get_most_smart_users):
            with self.subTest(ranking=ranking.__name__), patch.object(
                self.executor, "execute", wraps=self.executor.execute
            ) as execute:
                records = list(ranking())
                self.assertEqual([record.user.discord_id for record in records], [
                                 str(id) for id in range(15, 5, -1)])
                self.assertEqual(execute.call_count, 2)

    def test_pending_rankings_keep_independent_order_and_filters(self):
        self.create_member(1, level=10, monthly_point=1)
        self.create_member(2, level=1, monthly_point=100)
        level = self.guild.get_top_users()
        monthly = self.guild.get_monthly_top_users()
        self.assertEqual(
            [record.user.discord_id for record in monthly], ["2", "1"])
        self.assertEqual(
            [record.user.discord_id for record in level], ["1", "2"])

    def test_guild_list_prefetches_related_guilds(self):
        record = self.create_member(1)
        GuildUser.createOrFail(user_id=record.user_id, guild=self.other_guild)
        user = User.find(record.user_id)
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            self.assertEqual([item.guild.discord_id for item in user.guildusers.withRelations(
                "guild")], ["1000", "2000"])
            self.assertEqual(execute.call_count, 2)

    def test_profile_layouts_include_only_shared_and_current_guild(self):
        attributes = ProfileLayout.default()._modified_attributes
        shared = ProfileLayout.createOrFail(**{**attributes, "name": "Shared"})
        own = ProfileLayout.createOrFail(
            **{**attributes, "name": "Own", "guild_id": self.guild.id})
        ProfileLayout.createOrFail(
            **{**attributes, "name": "Other", "guild_id": self.other_guild.id})
        self.assertEqual({layout.id for layout in ProfileLayout.available_for_guild(
            self.guild.id)}, {shared.id, own.id})

    def test_ranking_indexes_are_used_without_sorting_a_whole_table(self):
        for order, index in (("monthly_point DESC", "idx_guildusers_monthly_top"),
                             ("level DESC, point DESC",
                              "idx_guildusers_level_top"),
                             ("smartpoint DESC", "idx_guildusers_smartpoint_top")):
            with self.subTest(order=order):
                plan = self.executor.execute(
                    f"EXPLAIN QUERY PLAN SELECT * FROM guildusers WHERE guild_id=? ORDER BY {order} LIMIT 10",
                    [self.guild.id], many=True)
                details = " ".join(row["detail"] for row in plan)
                self.assertIn(index, details)
                self.assertNotIn("TEMP B-TREE", details)

    def test_index_migration_can_be_rolled_back_and_reapplied_without_data_loss(self):
        record = self.create_member(1, smartpoint=75)
        migration = importlib.import_module(
            "libs.databases.migrations.20261027000000_optimize_database_queries")
        rollback(1)
        for _, index, _ in migration.OptimizeDatabaseQueries.indexes:
            self.assertIsNone(self.executor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?", [index]))
        self.assertEqual(GuildUser.find(record.id).smartpoint, 75)
        migrate()
        migrate()
        for _, index, _ in migration.OptimizeDatabaseQueries.indexes:
            self.assertIsNotNone(self.executor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?", [index]))
        self.assertEqual(GuildUser.find(record.id).smartpoint, 75)

    def test_index_rollback_uses_mariadb_syntax(self):
        migration = importlib.import_module(
            "libs.databases.migrations.20261027000000_optimize_database_queries")
        with patch.object(migration.DBConfig, "get", return_value="mariadb"), patch.object(migration, "executor_select") as select:
            migration.OptimizeDatabaseQueries().rollback()
        self.assertEqual(select.return_value.commit.call_args_list[0].args,
                         ("DROP INDEX idx_profilelayouts_guild ON profilelayouts",))


if __name__ == "__main__":
    unittest.main()
