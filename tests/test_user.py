import unittest
from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.profile_layout import ProfileLayout

from libs.databases.model.user import User
from libs.databases.model.wallpaper import Wallpaper
from tests.utils import Utils


class TestUser(unittest.TestCase):
    __user: User

    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        self.__user = User("TestUser")

    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")

    def test_get_root_users(self):
        self.assertTrue(len(User.get_root_users()) >= 0)

    def test_get_top_users(self):
        self.assertTrue(len(User.get_top_users()) >=
                        0 and len(User.get_top_users()) <= 10)

    def test_get_5_monthly_most_active_users(self):
        self.assertFalse(len(User.get_5_monthly_most_active_users()) > 5)

    def test_get_discord_id(self):
        self.assertEqual(self.__user.discord_id, "TestUser")

    def test_get_level(self):
        self.__user.reset_level()
        self.assertEqual(self.__user.level, 1)

    def test_get_point(self):
        self.__user.reset_point()
        self.assertEqual(self.__user.point, 0)

    def test_get_smartpoint(self):
        self.assertEqual(self.__user.smartpoint, 20)

    def test_add_point(self):
        self.__user.reset_point()
        self.__user.add_point(3)
        self.assertEqual(self.__user.point, 3)

    def test_add_remove_smartpoint(self):
        self.__user.add_smartpoint(10)
        self.assertEqual(self.__user.smartpoint, 30)
        self.__user.remove_smartpoint(10)
        self.assertEqual(self.__user.smartpoint, 20)

    def test_get_name_color(self):
        self.assertEqual(self.__user.name_color, "#0000FF")

    def test_get_bar_color(self):
        self.assertEqual(self.__user.bar_color, "#ADFF2F")

    def test_change_user_bar_color(self):
        self.__user.change_bar_color("#FF0000")
        self.assertEqual(self.__user.bar_color, "#FF0000")
        self.__user.change_bar_color("#ADFF2F")

    def test_change_user_name_color(self):
        self.__user.change_name_color("#FF0000")
        self.assertEqual(self.__user.name_color, "#FF0000")
        self.__user.change_name_color("#0000FF")

    def test_level_up(self):
        self.__user.reset_level()
        self.__user.reset_point()
        self.__user.add_point(200)
        self.assertEqual(self.__user.level, 2)
        self.assertEqual(self.__user.point, 0)
        self.__user.remove_smartpoint(200)

    def test_is_root(self):
        self.assertEqual(self.__user.is_root, False)

    def test_toggle_root(self):
        self.__user.toggle_root()
        self.assertEqual(self.__user.is_root, True)
        self.__user.toggle_root()
        self.assertEqual(self.__user.is_root, False)
        self.__user.toggle_root(True)
        self.assertEqual(self.__user.is_root, True)
        self.__user.toggle_root(False)
        self.assertEqual(self.__user.is_root, False)

    def test_get_badges_list(self):
        self.assertEqual(self.__user.badges_list, [])

    def test_current_wallpaper(self):
        self.assertEqual(self.__user.current_wallpaper.name, "default")

    def test_list_of_posseded_wallpaper(self):
        list_of_wallpaper_name = []
        for wallpaper in self.__user.list_of_posseded_wallpapers:
            list_of_wallpaper_name.append(wallpaper.name)
        self.assertTrue("default" in list_of_wallpaper_name)

    def test_add_posseded_wallpaper(self):
        Utils.add_test_wallpaper("test12345")
        wallpaper = Wallpaper("test12345")

        self.__user.add_posseded_wallpaper(wallpaper)

        list_of_posseeded_wallpaper = self.__user.list_of_posseded_wallpapers
        Utils.wallpaper_in_list_of_wallpaper(
            "test12345", list_of_posseeded_wallpaper)
        Utils.wallpaper_in_list_of_wallpaper(
            "default", list_of_posseeded_wallpaper)

        Wallpaper.remove(wallpaper)

    def test_increase_number_of_buy(self):
        self.__user.increase_number_of_buy()
        self.__user.increase_number_of_buy()
        self.__user.increase_number_of_buy()
        self.assertEqual(self.__user.number_of_buy, 3)
        self.__user.reset_number_of_buy()
        self.assertEqual(self.__user.number_of_buy, 0)

    def test_buy_wallpaper(self):
        Utils.add_test_wallpaper("test12345")
        wallpaper = Wallpaper("test12345")

        self.__user.buy_wallpaper(wallpaper)

        list_of_posseeded_wallpaper = self.__user.list_of_posseded_wallpapers
        Utils.wallpaper_in_list_of_wallpaper(
            "test12345", list_of_posseeded_wallpaper)
        Utils.wallpaper_in_list_of_wallpaper(
            "default", list_of_posseeded_wallpaper)

        self.assertEqual(self.__user.smartpoint, 10)
        self.__user.add_smartpoint(10)
        self.assertEqual(self.__user.smartpoint, 20)

        Wallpaper.remove(wallpaper)

    def test_get_user_profile_layout(self):
        self.assertEqual(str(self.__user.profiles_layout),
                         str(ProfileLayout.get_default()))

    def test_change_user_profile_layout(self):
        profile_layout_name = "test_add_profile_layout"
        self.assertEqual(str(self.__user.profiles_layout),
                         str(ProfileLayout.get_default()))
        Utils.add_profile_layout(profile_layout_name)
        profile_layout = ProfileLayout(profile_layout_name)
        self.__user.change_profile_layout(profile_layout)
        self.assertEqual(str(self.__user.profiles_layout),
                         str(ProfileLayout(profile_layout_name)))

        self.__user.change_profile_layout(ProfileLayout.get_default())
        ProfileLayout.remove(profile_layout)

    def test_has_user_accepted_rules(self):
        self.assertEqual(self.__user.has_accepted_rules, False)

    def test_toggle_user_accepted_rules(self):
        self.__user.toggle_accepted_rules()
        self.assertEqual(self.__user.has_accepted_rules, True)
        self.__user.toggle_accepted_rules()

    def test_toggle_user_accepted_rules(self):
        self.__user.toggle_accepted_rules(True)
        self.assertEqual(self.__user.has_accepted_rules, True)
        self.__user.toggle_accepted_rules(False)

    def test_user_reset_monthly_point(self):
        self.__user.add_point(10)
        self.__user.reset_monthly_point()
        self.assertEqual(self.__user.monthly_point, 0)

    def test_user_add_monthly_point(self):
        self.__user.add_monthly_point(10)
        self.assertEqual(self.__user.monthly_point, 10)
        self.__user.reset_monthly_point()

    def test_user_remove_monthly_point(self):
        self.__user.add_monthly_point(10)
        self.__user.remove_monthly_point(5)

        self.assertEqual(self.__user.monthly_point, 5)
        self.__user.reset_monthly_point()
