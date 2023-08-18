import unittest

from libs.databases.wallpaper import Wallpaper

class TestWallpaper(unittest.TestCase):
    __wallpaper : Wallpaper
    
    def __init__(self, methodName: str = "runTest") -> None:
        self.__wallpaper = Wallpaper("default")
        super().__init__(methodName)
    
    def test_get_name(self):
        self.assertEqual(self.__wallpaper.name, "default")
        
    def test_price_level(self):
        self.assertEqual(self.__wallpaper.level, 0)
        self.assertEqual(self.__wallpaper.price, 0)
    
    def test_url(self):
        self.assertTrue(isinstance(self.__wallpaper.url, str))