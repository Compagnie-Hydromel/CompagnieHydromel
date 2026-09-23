from MIWOS.migration import Migration


class CreateScheduledMessages(Migration):
    def migrate(self):
        with self.create_tables("scheduledmessages") as x:
            x.primary_key("id", auto_increment=True)
            x.string("name", null=False)
            x.string("channel_id", null=False)
            x.string("message", null=False)
            x.string("day", null=False)
            x.string("time", null=False)
            x.string("timezone", null=False)
            x.string("last_sent_date")
            x.string("attachment_path")
            x.string("attachment_name")
            x.references("guild", null=False, on_delete="CASCADE")
            x.unique("name", "guild_id")

    def rollback(self):
        self.drop_tables("scheduledmessages")
