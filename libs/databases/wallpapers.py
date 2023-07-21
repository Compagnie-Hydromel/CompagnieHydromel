from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess

class Wallpapers:
    __db_access : DatabaseAccessImplement

    def __init__(self) -> None:
        self.__db_access = SqliteAccess()

    def all(self) -> None:
        return self.__db_access.get_all_wallpapers()
    
    def is_exist(self, wallpaper_name: str) -> bool:
        return self.__db_access.is_wallpaper_exist(wallpaper_name)
