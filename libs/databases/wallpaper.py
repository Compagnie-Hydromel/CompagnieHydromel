from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.exception.wallpaper.wallpaper_not_exist_exception import WallpaperNotExistException


class Wallpaper:
    """This class is designed to manage a wallpaper.
    """
    __wallpaper_name : str
    __db_access : DatabaseAccessImplement
    
    def __init__(self, wallpaper_name : str) -> None:
        """This method is designed to initialize the Wallpaper class.

        Args:
            wallpaper_name (str): The wallpaper name.

        Raises:
            WallpaperNotExistException: Raise when a wallpaper not exist.
        """        
        self.__wallpaper_name = wallpaper_name
        self.__db_access = SqliteAccess()

        if not self.__db_access.is_wallpaper_exist(self.__wallpaper_name):
            raise WallpaperNotExistException

    @property
    def name(self) -> str:
        """This method is designed to get the wallpaper name.

        Returns:
            str: The wallpaper name.
        """
        return self.__wallpaper_name
    
    @property
    def price(self) -> int:
        """This method is designed to get the wallpaper price.

        Returns:
            int: The wallpaper price.
        """
        return self.__db_access.get_wallpaper_price(self.__wallpaper_name)
    
    @property
    def level(self) -> int:
        """This method is designed to get the wallpaper level.

        Returns:
            int: The wallpaper level.
        """
        return self.__db_access.get_wallpaper_level(self.__wallpaper_name)
    
    @property
    def url(self) -> str:
        """This method is designed to get the wallpaper url.

        Returns:
            str: The wallpaper url.
        """
        return self.__db_access.get_wallpaper_url(self.__wallpaper_name)
    

