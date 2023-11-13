import unittest
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout

from libs.databases.model.profile_layout.profile_layout import ProfileLayout
from libs.databases.model.profile_layout.profile_layouts import ProfileLayouts


class TestProfileLayout(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        self.__profile_layout = ProfileLayout.get_default()
        self.__profile_layouts = ProfileLayouts()
        super().__init__(methodName)
    
    def test_name(self):
        __old_name = self.__profile_layout.name
        __name = "default"
        self.__profile_layouts.rename(self.__profile_layout, __name)
        self.__profile_layout = ProfileLayout.get_default()
        self.assertEqual(self.__profile_layout.name, __name)
        self.__profile_layouts.rename(self.__profile_layout, __old_name)
        
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
        self.__profile_layouts.update(self.__profile_layout, __layout)
        self.assertEqual(str(self.__profile_layout.layout), str(__layout))
        self.__profile_layouts.update(self.__profile_layout, __old_layout)