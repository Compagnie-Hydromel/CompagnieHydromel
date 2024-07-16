import unittest

from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.wallpaper.wallpaper import Wallpaper
from tests.utils import Utils

class TestWallpaper(unittest.TestCase):
    __wallpaper : Wallpaper
        
    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        self.__wallpaper = Wallpaper.get_default()
    
    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")

    def test_get_name(self):
        __old_name = self.__wallpaper.name
        __name = "default"
        self.__wallpaper.name = __name
        self.assertEqual(self.__wallpaper.name, __name)
        self.__wallpaper.name = __old_name
        self.assertEqual(self.__wallpaper.name, __old_name)
        
    def test_price_level(self):
        self.__old_price = self.__wallpaper.price
        self.__old_level = self.__wallpaper.level
        self.__price = 100
        self.__level = 1
        self.__wallpaper.price = self.__price
        self.__wallpaper.level = self.__level
        self.assertEqual(self.__wallpaper.level, self.__level)
        self.assertEqual(self.__wallpaper.price, self.__price)
        self.__wallpaper.price = self.__old_price
        self.__wallpaper.level = self.__old_level
        self.assertEqual(self.__wallpaper.level, self.__old_level)
        self.assertEqual(self.__wallpaper.price, self.__old_price)
    
    def test_url(self):
        self.assertTrue(isinstance(self.__wallpaper.url, str))
        self.assertNotEqual(self.__wallpaper.url, "")
        self.__old_url = self.__wallpaper.url
        self.__url = "https://shkermit.ch/~ethann/compHydromel/wallpapers/default.png"
        self.__wallpaper.url = self.__url
        self.assertEqual(self.__wallpaper.url, self.__url)
        self.__wallpaper.url = self.__old_url
        self.assertEqual(self.__wallpaper.url, self.__old_url)
        
    def test_wallpaper_url_not_an_image(self):
        with self.assertRaises(Exception):
            self.__wallpaper.url = "https://google.com"