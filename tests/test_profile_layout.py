import unittest
from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout

from libs.databases.model.profile_layout import ProfileLayout
from libs.exception.profile_layout.cannot_remove_default_profile_layout import CannotRemoveDefaultProfileLayout
from tests.utils import Utils


class TestProfileLayout(unittest.TestCase):
    __profile_layout: ProfileLayout

    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        self.__profile_layout = ProfileLayout.get_default()

    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")

    def test_name(self):
        __old_name = self.__profile_layout.name
        __name = "default"
        self.__profile_layout.name = __name
        self.__profile_layout = ProfileLayout.get_default()
        self.assertEqual(self.__profile_layout.name, __name)
        self.__profile_layout.name = __old_name

    def test_layout(self):
        __old_layout = self.__profile_layout.layout
        __layout = Layout(
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
        )
        self.__profile_layout.layout = __layout
        self.assertEqual(str(self.__profile_layout.layout), str(__layout))
        self.__profile_layout.layout = __old_layout

    def test_add_remove_profile_layout(self):
        profile_layout_name = "test_add_profile_layout"

        layout = Utils.add_profile_layout(profile_layout_name)

        if self.__contains_profile_layout(profile_layout_name):
            self.assertEqual(
                str(ProfileLayout(profile_layout_name).layout), str(layout))
            ProfileLayout.remove(ProfileLayout(profile_layout_name))
        else:
            self.assertTrue(False)

    def test_cannot_remove_default_profile_layout(self):
        with self.assertRaises(CannotRemoveDefaultProfileLayout):
            ProfileLayout.remove(ProfileLayout.get_default())

    def __contains_profile_layout(self, name: str) -> bool:
        for profile_layout in ProfileLayout.all():
            if profile_layout.name == name:
                return True
        return False
