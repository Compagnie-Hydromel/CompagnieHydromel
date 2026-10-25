import unittest

from libs.databases.models.guild_user import GuildUser
from libs.projections.guild_user_projection import GuildUserProjection


class TestProfileColors(unittest.TestCase):
    def member(self, name_color="12AB34", bar_color="56CD78"):
        member = object.__new__(GuildUser)
        member._attributes = {"name_color": name_color, "bar_color": bar_color}
        member._modified_attributes = {}
        return member

    def test_database_colors_have_css_prefix(self):
        member = self.member()
        self.assertEqual(member.name_color, "#12AB34")
        self.assertEqual(member.bar_color, "#56CD78")

    def test_prefixed_colors_do_not_get_duplicate_prefix(self):
        member = self.member("#123456", "#ABCDEF")
        self.assertEqual(member.name_color, "#123456")
        self.assertEqual(member.bar_color, "#ABCDEF")

    def test_unsaved_colors_take_precedence(self):
        member = self.member()
        member.name_color = "#987654"
        member.bar_color = "FEDCBA"
        self.assertEqual(member.name_color, "#987654")
        self.assertEqual(member.bar_color, "#FEDCBA")

    def test_validation_and_reload_keep_selected_colors(self):
        member = self.member()
        member.name_color = "#987654"
        member.bar_color = "#FEDCBA"
        member.beforeValidation()
        self.assertEqual(member._modified_attributes["name_color"], "987654")
        self.assertEqual(member._modified_attributes["bar_color"], "FEDCBA")

        reloaded = self.member(**member._modified_attributes)
        self.assertEqual(reloaded.name_color, "#987654")
        self.assertEqual(reloaded.bar_color, "#FEDCBA")

    def test_missing_colors_use_profile_defaults(self):
        member = self.member(None, "")
        self.assertEqual(member.name_color, "#0000FF")
        self.assertEqual(member.bar_color, "#ADFF2F")

    def test_projection_returns_current_colors(self):
        class ProfileMember(GuildUser):
            @property
            def avatar_url(self):
                return "https://example.com/avatar.png"

            @property
            def display_name(self):
                return "Display name"

            @property
            def username(self):
                return "username"

        from types import SimpleNamespace

        member = object.__new__(ProfileMember)
        member._attributes = {
            "id": 1, "monthly_point": 0, "level": 1, "smartpoint": 20,
            "point": 0, "name_color": "12AB34", "bar_color": "56CD78",
            "wallpaper": SimpleNamespace(id=1, name="Forest", url="forest.png"),
            "user": SimpleNamespace(badges=[]),
        }
        member._modified_attributes = {}
        projection = GuildUserProjection.from_guild_user(member)
        self.assertEqual(projection.name_color, "#12AB34")
        self.assertEqual(projection.bar_color, "#56CD78")
