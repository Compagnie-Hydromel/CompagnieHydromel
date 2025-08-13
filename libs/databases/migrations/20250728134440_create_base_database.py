from MIWOS.migration import Migration


class CreateBaseDatabase(Migration):
    def migrate(self):
        with self.create_tables("guilds") as x:
            x.primary_key("id", auto_increment=True)
            x.string("discord_id", unique=True)
            x.string("information_channel_id")
            x.string("monthlytop_channel_id")

        with self.create_tables("badges") as x:
            x.primary_key("id", auto_increment=True)
            x.string("name", null=False)
            x.string("url", null=False)

        with self.create_tables("roles") as x:
            x.primary_key("id", auto_increment=True)
            x.string("discord_id", unique=True)
            x.integer("level", null=False)
            x.references("guild", null=False, on_delete="CASCADE")
            x.unique("guild_id", "level")

        with self.create_tables("wallpapers") as x:
            x.primary_key("id", auto_increment=True)
            x.string("name", null=False)
            x.string("url", null=False)
            x.integer("level", null=False)
            x.integer("price", null=False)
            x.references("guild", null=False, on_delete="CASCADE")
            x.unique("name", "guild_id")

        with self.create_tables("users") as x:
            x.primary_key("id", auto_increment=True)
            x.string("discord_id", unique=True)
            x.boolean("is_superadmin", null=False, default=False)

        with self.create_tables("profilelayouts") as x:
            x.primary_key("id", auto_increment=True)
            x.string("name", null=False)
            x.integer("profil_picture_x", null=False)
            x.integer("profil_picture_y", null=False)
            x.integer("name_x", null=False)
            x.integer("name_y", null=False)
            x.integer("username_x", null=False)
            x.integer("username_y", null=False)
            x.integer("level_x", null=False)
            x.integer("level_y", null=False)
            x.integer("badge_x", null=False)
            x.integer("badge_y", null=False)
            x.integer("level_bar_x", null=False)
            x.integer("level_bar_y", null=False)

        with self.create_tables("guildusers") as x:
            x.primary_key("id", auto_increment=True)
            x.references("guild", null=False, on_delete="CASCADE")
            x.references("user", null=False, on_delete="CASCADE")
            x.integer("point", null=False, default=0)
            x.integer("monthly_point", null=False, default=0)
            x.integer("level", null=False, default=1)
            x.integer("smartpoint", null=False, default=20)
            x.references("wallpaper", on_delete="SET NULL")
            x.string("bar_color", null=False, default="ADFF2F")
            x.string("name_color", null=False, default="0000FF")
            x.integer("number_of_buy", null=False, default=0)
            x.references("profilelayout", on_delete="SET NULL")
            x.boolean("has_accepted_rules", null=False, default=False)
            x.boolean("is_admin", null=False, default=False)
            x.unique("guild_id", "user_id")

        self.create_join_table(
            "users", "badges",
            can_have_duplicates=True,
            verb="deserve",
        )

        self.create_join_table(
            "guildusers", "wallpapers",
            verb="buy",
        )

    def rollback(self):
        self.drop_join_table(
            "users", "badges", verb="deserve"
        )
        self.drop_join_table(
            "guildusers", "wallpapers", verb="buy"
        )
        self.drop_tables(
            "guildusers",
            "profilelayouts",
            "wallpapers",
            "roles",
            "badges",
            "users",
            "guilds"
        )
