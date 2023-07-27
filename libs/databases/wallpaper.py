from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException


class Wallpaper:
    __wallpaper_name : str
    __db_access : DatabaseAccessImplement
    
    def __init__(self, wallpaper_name : str) -> None:
        self.__wallpaper_name = wallpaper_name
        self.__db_access = SqliteAccess()

        if not self.__db_access.is_wallpaper_exist(self.__wallpaper_name):
            raise WallpaperNotExistException

    def name(self) -> str:
        return self.__wallpaper_name
    
    def price(self) -> int:
        return self.__db_access.get_wallpaper_price(self.__wallpaper_name)
    
    def level(self) -> int:
        return self.__db_access.get_wallpaper_level(self.__wallpaper_name)
    
    def url(self) -> str:
        return self.__db_access.get_wallpaper_url(self.__wallpaper_name)
    

