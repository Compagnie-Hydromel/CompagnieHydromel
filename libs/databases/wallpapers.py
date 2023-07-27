from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.databases.wallpaper import Wallpaper

class Wallpapers:
    __db_access : DatabaseAccessImplement

    def __init__(self) -> None:
        self.__db_access = SqliteAccess()

    def all(self) -> None:
        return self.create_list_wallpaper_by_list_name(self.__db_access.get_all_wallpapers())
    
    def create_list_wallpaper_by_list_name(self, list_name: list) -> list:
        list_of_wallpapers = []

        for wallpaper in list_name:
            list_of_wallpapers.append(Wallpaper(wallpaper))

        return list_of_wallpapers
