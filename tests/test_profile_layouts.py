import unittest
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.model.profile_layout.profile_layout import ProfileLayout

from libs.databases.model.profile_layout.profile_layouts import ProfileLayouts
from libs.exception.profile_layout.cannot_remove_default_profile_layout import CannotRemoveDefaultProfileLayout
from tests.utils import Utils

class TestProfileLayout(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        self.__profile_layouts = ProfileLayouts()
        super().__init__(methodName)
        
    def test_add_remove_profile_layout(self):
        profile_layout_name = "test_add_profile_layout"

        layout = Utils.add_profile_layout(profile_layout_name)

        if self.__contains_profile_layout(profile_layout_name):
            self.assertEqual(str(ProfileLayout(profile_layout_name).layout), str(layout))
            self.__profile_layouts.remove(ProfileLayout(profile_layout_name))
        else:
            self.assertTrue(False)
        
    def test_cannot_remove_default_profile_layout(self):
        with self.assertRaises(CannotRemoveDefaultProfileLayout):
            self.__profile_layouts.remove(ProfileLayout.get_default())
        
    def __contains_profile_layout(self, name: str) -> bool:
        for profile_layout in self.__profile_layouts.get_all_profile_layouts:
            if profile_layout.name == name:
                return True
        return False