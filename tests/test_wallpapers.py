import unittest

from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.wallpaper.wallpaper import Wallpaper
from libs.databases.model.wallpaper.wallpapers import Wallpapers
from libs.exception.wallpaper.wallpaper_already_exist_exception import WallpaperAlreadyExistException
from tests.utils import Utils

class TestWallpapers(unittest.TestCase):
    __wallpapers : Wallpapers
    
    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        self.__wallpapers = Wallpapers()

    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")
        
    def test_all(self):
        self.assertTrue(len(self.__wallpapers.all) > 0)
        
    def test_add_remove(self):
        self.__wallpapers.add("test", "test", 0, 0)
        for wallapper in self.__wallpapers.all:
            if wallapper.name == "test":
                self.__wallpapers.remove(wallapper)
                self.assertTrue(True)
                return
        self.assertTrue(False)
        
    def test_exception_add_already_exist(self):
        self.__wallpapers.add("test", "test", 0, 0)
        try: 
            self.__wallpapers.add("test", "test", 0, 0)
            self.assertTrue(False)
        except WallpaperAlreadyExistException:
            self.assertTrue(True)
            self.__wallpapers.remove(Wallpaper("test"))
