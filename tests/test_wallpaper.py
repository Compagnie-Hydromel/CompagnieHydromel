import unittest

from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers

class TestWallpaper(unittest.TestCase):
    __wallpaper : Wallpaper
    
    def test_get_name(self):
        self.__wallpaper = Wallpaper("default")
        self.assertEqual(self.__wallpaper.name(), "default")
        
    # TODO : Add more tests.