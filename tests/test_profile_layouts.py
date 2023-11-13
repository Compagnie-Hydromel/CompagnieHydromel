import unittest
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.model.profile_layout.profile_layout import ProfileLayout

from libs.databases.model.profile_layout.profile_layouts import ProfileLayouts

class TestProfileLayout(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        self.__profile_layouts = ProfileLayouts()
        super().__init__(methodName)
        
    def test_add_remove_profile_layout(self):
        layout = self.__add_profile_layout()
        profile_layout_name = "test_add_profile_layout"
        if self.__contains_profile_layout(profile_layout_name):
            self.assertEqual(str(ProfileLayout(profile_layout_name).layout), str(layout))
            self.__profile_layouts.remove(ProfileLayout(profile_layout_name))
        else:
            self.assertTrue(False)
        
    def test_rename_profile_layout(self):
        self.__add_profile_layout()
        profile_layout_old_name = "test_add_profile_layout"
        profile_layout_new_name = "test_rename_profile_layout"
        
        self.__profile_layouts.rename(ProfileLayout(profile_layout_old_name), profile_layout_new_name)
        
        self.assertFalse(self.__contains_profile_layout(profile_layout_old_name))
        self.assertTrue(self.__contains_profile_layout(profile_layout_new_name))
        
        self.__profile_layouts.remove(ProfileLayout(profile_layout_new_name))
        
        self.assertFalse(self.__contains_profile_layout(profile_layout_new_name))
        
    def __contains_profile_layout(self, name: str) -> bool:
        for profile_layout in self.__profile_layouts.get_all_profile_layouts:
            if profile_layout.name == name:
                return True
        return False
        
    def __add_profile_layout(self) -> Layout:
        layout: Layout = Layout(
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
        )
        self.__profile_layouts.add("test_add_profile_layout", layout)
        return layout