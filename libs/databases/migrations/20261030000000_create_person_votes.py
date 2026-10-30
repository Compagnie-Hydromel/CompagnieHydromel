from MIWOS.config import DBConfig
from MIWOS.libs.sql.select import executor_select
from MIWOS.migration import Migration


class CreatePersonVotes(Migration):
    def migrate(self):
        with self.create_tables("personvotes") as x:
            x.primary_key("id", auto_increment=True)
            x.string("guild_discord_id", null=False)
            x.string("channel_id", null=False)
            x.string("message_id")
            x.string("title", null=False)
            x.string("candidates", null=False)
            x.integer("votes_per_member", null=False)
            x.bigint("expires_at", null=False)
            x.boolean("anonymous", null=False)
            x.boolean("allow_multiple", null=False)
            x.boolean("closed", null=False)
            x.string("salt", null=False)
        if DBConfig.get("db_connector") != "sqlite":
            # A full server membership snapshot can exceed MariaDB's TEXT limit.
            executor_select().commit(
                "ALTER TABLE personvotes MODIFY candidates LONGTEXT NOT NULL")
        with self.create_tables("personballots") as x:
            x.primary_key("id", auto_increment=True)
            x.references("personvote", null=False, on_delete="CASCADE")
            x.string("voter_key", null=False)
            x.string("allocations", null=False)
            x.unique("personvote_id", "voter_key")

    def rollback(self):
        self.drop_tables("personballots")
        self.drop_tables("personvotes")
