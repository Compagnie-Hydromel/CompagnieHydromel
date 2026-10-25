from MIWOS.migration import Migration
from MIWOS.libs.sql.select import executor_select


class ScopeProfileLayoutsToGuilds(Migration):
    def migrate(self):
        # Legacy layouts remain shared; newly created layouts belong to a guild.
        executor_select().commit(
            "ALTER TABLE profilelayouts ADD COLUMN guild_id INTEGER NULL")

    def rollback(self):
        executor_select().commit(
            "DELETE FROM profilelayouts WHERE guild_id IS NOT NULL")
        executor_select().commit(
            "ALTER TABLE profilelayouts DROP COLUMN guild_id")
