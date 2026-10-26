from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from libs.utils.utils import Utils


controller = Utils.import_module_from_path(
    "profile_controller", "http/controllers/profile_controller.py")


def make_wallpaper(id=1, guild_id=10, price=15, level=0):
    return SimpleNamespace(id=id, guild_id=guild_id, price=price,
                           level=level, name="Forest", url="https://example.com/forest.png")


class TestProfileValidation(unittest.TestCase):
    def test_colors_are_validated_and_normalized(self):
        changes = controller.ProfileUpdate(
            name_color="blue", bar_color="#ABCDEF")
        self.assertEqual(changes.name_color, "#0000FF")
        self.assertEqual(changes.bar_color, "#ABCDEF")

    def test_rejects_invalid_colors_ids_and_extra_attributes(self):
        for changes in ({"name_color": "not-a-color"}, {"bar_color": ""},
                        {"wallpaper_id": 0}, {"layout_id": -1}, {"smartpoint": 999}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                controller.ProfileUpdate.model_validate({
                    "name_color": "blue", "bar_color": "green", **changes})

    def test_membership_lookup_never_creates_a_member(self):
        request, user, member = Mock(), Mock(), Mock()
        with patch.object(controller.HTTPUtils, "get_user_from_session", return_value=user), patch.object(
            controller.GuildUser, "whereFirst", return_value=member
        ) as lookup:
            self.assertIs(controller.get_member(request, 10), member)
        lookup.assert_called_once_with(user=user, guild_id=10)

    def test_denies_access_to_other_guilds(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session"), patch.object(
            controller.GuildUser, "whereFirst", return_value=None
        ), self.assertRaises(HTTPException) as error:
            controller.get_member(Mock(), 10)
        self.assertEqual(error.exception.status_code, 403)

    def test_requires_session_before_membership_lookup(self):
        with patch.object(controller.HTTPUtils, "get_user_from_session", side_effect=HTTPException(401)), patch.object(
            controller.GuildUser, "whereFirst"
        ) as lookup, self.assertRaises(HTTPException) as error:
            controller.get_member(Mock(), 10)
        self.assertEqual(error.exception.status_code, 401)
        lookup.assert_not_called()

    def test_catalog_contains_ownership_prices_and_layout_coordinates(self):
        owned, locked = make_wallpaper(), make_wallpaper(id=2, price=0, level=5)
        layout = SimpleNamespace(id=None, name="default", guild_id=None, profil_picture_x=0,
                                 profil_picture_y=0, **{key: 0 for key in (
                                     "name_x", "name_y", "username_x", "username_y", "level_x",
                                     "level_y", "badge_x", "badge_y", "level_bar_x", "level_bar_y")})
        member = SimpleNamespace(guild_id=10, wallpapers=[owned], wallpaper=owned,
                                 profilelayout=None, guild=SimpleNamespace(wallpapers=[owned, locked]))
        with patch.object(controller.GuildUserProjection, "from_guild_user", return_value={"smartpoint": 20}), patch.object(
            controller.ProfileLayout, "available_for_guild", return_value=[layout]
        ), patch.object(controller.ProfileLayout, "default", return_value=layout), patch.object(
            controller.Wallpaper, "default", return_value=SimpleNamespace(url="default.png")
        ):
            data = controller.profile_data(member)
        self.assertTrue(data["wallpapers"][0]["owned"])
        self.assertFalse(data["wallpapers"][1]["owned"])
        self.assertEqual(data["wallpapers"][0]["price"], 15)
        self.assertEqual(data["wallpapers"][1]["level"], 5)
        self.assertEqual(data["default_layout"]["profile_picture_x"], 0)
        self.assertEqual(data["wallpaper_id"], 1)
        self.assertIsNone(data["layout_id"])


class TestProfileRoutes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.wallpaper = make_wallpaper()
        self.member = SimpleNamespace(
            wallpapers=[self.wallpaper], smartpoint=20,
            guild=SimpleNamespace(wallpapers=[self.wallpaper]),
            saveOrFail=Mock(), wallpaper=self.wallpaper, profilelayout=None)
        self.membership = patch.object(
            controller, "get_member", return_value=self.member)
        self.get_member = self.membership.start()
        self.addCleanup(self.membership.stop)
        self.projection = patch.object(
            controller, "profile_data", return_value={"updated": True})
        self.project = self.projection.start()
        self.addCleanup(self.projection.stop)

    async def test_get_profile_uses_current_member(self):
        request = Mock()
        self.assertEqual(await controller.show(request, 10), {"updated": True})
        self.get_member.assert_called_once_with(request, 10)
        self.project.assert_called_once_with(self.member)

    async def test_saves_colors_owned_wallpaper_and_layout(self):
        layout = Mock(id=3, guild_id=10)
        with patch.object(controller.ProfileLayout, "find", return_value=layout):
            await controller.update(Mock(), 10, controller.ProfileUpdate(
                name_color="red", bar_color="blue", wallpaper_id=1, layout_id=3))
        self.assertEqual(self.member.name_color, "#FF0000")
        self.assertEqual(self.member.bar_color, "#0000FF")
        self.assertIs(self.member.wallpaper, self.wallpaper)
        self.assertIs(self.member.profilelayout, layout)
        self.member.saveOrFail.assert_called_once_with()

    async def test_restores_default_wallpaper_and_layout(self):
        await controller.update(Mock(), 10, controller.ProfileUpdate(
            name_color="blue", bar_color="red"))
        self.assertIsNone(self.member.wallpaper)
        self.assertIsNone(self.member.profilelayout)

    async def test_rejects_unowned_or_other_guild_wallpaper(self):
        for id, guild_id in ((2, 10), (1, 11)):
            with self.subTest(id=id, guild_id=guild_id):
                self.wallpaper.guild_id = guild_id
                with self.assertRaises(HTTPException) as error:
                    await controller.update(Mock(), 10, controller.ProfileUpdate(
                        name_color="blue", bar_color="red", wallpaper_id=id))
                self.assertEqual(error.exception.status_code, 403)
        self.member.saveOrFail.assert_not_called()

    async def test_rejects_missing_layout_without_saving(self):
        with patch.object(controller.ProfileLayout, "find", return_value=None), self.assertRaises(HTTPException) as error:
            await controller.update(Mock(), 10, controller.ProfileUpdate(
                name_color="blue", bar_color="red", layout_id=99))
        self.assertEqual(error.exception.status_code, 404)
        self.member.saveOrFail.assert_not_called()

    async def test_rejects_layout_from_another_guild(self):
        with patch.object(controller.ProfileLayout, "find", return_value=Mock(guild_id=11)), self.assertRaises(HTTPException) as error:
            await controller.update(Mock(), 10, controller.ProfileUpdate(
                name_color="blue", bar_color="red", layout_id=99))
        self.assertEqual(error.exception.status_code, 404)
        self.member.saveOrFail.assert_not_called()

    async def test_purchase_deducts_price_and_adds_wallpaper(self):
        self.member.wallpapers = []
        await controller.buy(Mock(), 10, 1)
        self.assertEqual(self.member.smartpoint, 5)
        self.assertEqual(self.member.wallpapers, [self.wallpaper])
        self.member.saveOrFail.assert_called_once_with()

    async def test_rejects_invalid_purchases_without_charging(self):
        cases = ((99, 15, 20, False, 404), (1, 15, 20, True, 409),
                 (1, 0, 20, False, 400), (1, 15, 5, False, 400))
        for id, price, balance, owned, status in cases:
            with self.subTest(id=id, price=price, balance=balance, owned=owned):
                self.wallpaper.price = price
                self.member.smartpoint = balance
                self.member.wallpapers = [self.wallpaper] if owned else []
                with self.assertRaises(HTTPException) as error:
                    await controller.buy(Mock(), 10, id)
                self.assertEqual(error.exception.status_code, status)
                self.assertEqual(self.member.smartpoint, balance)
        self.member.saveOrFail.assert_not_called()
