import unittest

from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers
from libs.exception.wallpaper_already_exist_exception import WallpaperAlreadyExistException

class TestWallpapers(unittest.TestCase):
    __wallpaper : Wallpapers
    
    def __init__(self, methodName: str = "runTest") -> None:
        self.__wallpapers = Wallpapers()
        super().__init__(methodName)
        
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
