from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.model.wallpaper.wallpaper import Wallpaper
from libs.exception.wallpaper.cannot_remove_default_wallpaper import CannotRemoveDefaultWallpaper
from libs.exception.wallpaper.wallpaper_already_exist_exception import WallpaperAlreadyExistException
from libs.exception.wallpaper.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper.wallpaper_url_not_an_image import WallpaperUrlNotAnImage
from libs.utils.utils import Utils

class Wallpapers:
    """This class is designed to manage wallpapers.
    """
    __db_access : DatabaseAccessImplement

    def __init__(self) -> None:
        """This method is designed to initialize the Wallpapers class. 
        """
        self.__db_access = DatabasesSelecter().databases

    @property
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
    
    def add(self, wallpaper_name: str, url: str, price: int = 0, level: int = 0) -> None:
        """This method is designed to add a wallpaper to the database.

        Args:
            wallpaper_name (str): the wallpaper name.
            url (str): the url of the wallpaper
            price (int, optional): the price of the wallpaper. Defaults to 0.
            level (int, optional): the level of the wallpaper. Defaults to 0.
    
        Raises:
            WallpaperAlreadyExistException: If the wallpaper already exist.
        """
        try: 
            Wallpaper(wallpaper_name)
            raise WallpaperAlreadyExistException
        except WallpaperNotExistException:
            if not (Utils.is_url_image(url) or Utils.is_url_animated_gif(url)):
                raise WallpaperUrlNotAnImage
            self.__db_access.add_wallpaper(wallpaper_name, url, price, level)
        
    def remove(self, wallpaper: Wallpaper):
        """This method is designed to remove a wallpaper from the database.

        Args:
            wallpaper (Wallpaper): The wallpaper to remove.
        """
        if wallpaper.name == Wallpaper.get_default().name:
            raise CannotRemoveDefaultWallpaper
        self.__db_access.remove_wallpaper(wallpaper.name)