from MIWOS.config import DBConfig
from MIWOS.libs.sql.select import executor_select
from MIWOS.migration import Migration


class OptimizeDatabaseQueries(Migration):
    indexes = (
        ("guildusers", "idx_guildusers_monthly_top", "guild_id, monthly_point"),
        ("guildusers", "idx_guildusers_level_top", "guild_id, level, point"),
        ("guildusers", "idx_guildusers_smartpoint_top", "guild_id, smartpoint"),
        ("guildusers", "idx_guildusers_user", "user_id"),
        ("profilelayouts", "idx_profilelayouts_guild", "guild_id"),
    )

    def migrate(self):
        for table, name, columns in self.indexes:
            executor_select().commit(
                f"CREATE INDEX {name} ON {table} ({columns})")

    def rollback(self):
        for table, name, _ in reversed(self.indexes):
            suffix = "" if DBConfig.get(
                "db_connector") == "sqlite" else f" ON {table}"
            executor_select().commit(f"DROP INDEX {name}{suffix}")
