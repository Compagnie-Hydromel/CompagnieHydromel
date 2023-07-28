from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.databases.wallpaper import Wallpaper

class Wallpapers:
    """This class is designed to manage wallpapers.
    """
    __db_access : DatabaseAccessImplement

    def __init__(self) -> None:
        """This method is designed to initialize the Wallpapers class. 
        """
        self.__db_access = SqliteAccess()

    def all(self) -> list[Wallpaper]:
        """This method is designed to get all wallpapers.

        Returns:
            list[Wallpaper]: A list of All Wallpaper object.
        """
        return self.create_list_wallpaper_by_list_name(self.__db_access.get_all_wallpapers())
    
    def create_list_wallpaper_by_list_name(self, list_name: list[str]) -> list[Wallpaper]:
        """This method is designed to create a list of Wallpaper object by a list of wallpaper name.

        Args:
            list_name (list[str]): A list of wallpaper name.

        Returns:
            list[Wallpaper]: A list of Wallpaper object.
        """
        list_of_wallpapers = []

        for wallpaper in list_name:
            list_of_wallpapers.append(Wallpaper(wallpaper))

        return list_of_wallpapers
