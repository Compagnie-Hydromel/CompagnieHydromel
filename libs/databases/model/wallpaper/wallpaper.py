import requests
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.repository.sqlite.sqlite_access import SqliteAccess
from libs.exception.wallpaper.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper.wallpaper_url_not_an_image import WallpaperUrlNotAnImage


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
        
    @staticmethod
    def get_default():
        """This method is designed to get the default wallpaper.

        Returns:
            Wallpaper: The default wallpaper.
        """
        return Wallpaper(SqliteAccess().get_default_wallpaper_name())

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
    
    @name.setter 
    def name(self, name : str) -> None:
        """This method is designed to set the wallpaper name.

        Args:
            name (str): The new wallpaper name.
        """
        self.__db_access.rename_wallpaper(self.__wallpaper_name, name)
        self.__wallpaper_name = name
            
    @price.setter
    def price(self, price : int) -> None:
        """This method is designed to set the wallpaper price.

        Args:
            price (int): The new wallpaper price.
        """
        self.__db_access.set_wallpaper_price(self.__wallpaper_name, price)
    
    @level.setter
    def level(self, level: int) -> None:
        """This method is designed to set the wallpaper level.

        Args:
            level (int): The new wallpaper level.
        """
        self.__db_access.set_wallpaper_level(self.__wallpaper_name, level)
        
    @url.setter
    def url(self, url : str) -> None:
        """This method is designed to set the wallpaper url.

        Args:
            url (str): The new wallpaper url.
        
        Raises:
            WallpaperUrlNotAnImage: Raise when the url is not an image.
        """
        if not self.__is_url_image(url):
            raise WallpaperUrlNotAnImage
        self.__db_access.set_wallpaper_url(self.__wallpaper_name, url)
    

    def __is_url_image(self, image_url):
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
        return False