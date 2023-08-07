import re
from libs.databases.badges import Badges
from libs.databases.database_access_implement import DatabaseAccessImplement, ProfileColoredPart
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.exception.not_enougt_smartcoin_exception import NotEnougtSmartcoinException
from libs.exception.wallpaper_already_posseded_exception import WallpaperAlreadyPossededException
from libs.exception.wallpaper_cannot_be_buyed_exception import WallpaperCannotBeBuyedException
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.utils import Utils

class User:
    """This class is designed to manage a single user.
    """
    __discord_id : str
    __db_access : DatabaseAccessImplement
    
    def __init__(self, discord_id : str) -> None:
        """This method is designed to initialize the User class.

        Args:
            discord_id (str): The discord id of the user.
        """
        self.__discord_id = discord_id
        self.__db_access = SqliteAccess()
        self.__db_access.add_user_if_not_exist(discord_id)
    
    def discord_id(self) -> str:
        """This method is designed to get the discord id of the user.

        Returns:
            str: The discord id of the user.
        """        
        return self.__discord_id
    
    def level(self) -> int:
        """This method is designed to get the level of the user.

        Returns:
            int: The level of the user.
        """
        return self.__db_access.get_user_level(self.__discord_id)

    def point(self) -> int:
        """This method is designed to get the point of the user.

        Returns:
            int: The point of the user.
        """
        return self.__db_access.get_user_point(self.__discord_id)
    
    def add_point(self, point : int = 1) -> None:
        """This method is designed to add point to the user.

        Args:
            point (int, optional): Number of point to add. Defaults to 1.
        """
        self.__db_access.add_user_point(self.__discord_id, point)
        self.__check_add_level_up()

    def add_smartcoin(self, amount : int = 1) -> None: 
        """This method is designed to add smartcoin to the user.

        Args:
            amount (int, optional): Number of smartcoin to add. Defaults to 1.
        """
        self.__db_access.add_smartcoin(self.__discord_id, amount)

    def remove_smartcoin(self, amount : int = 1) -> None:
        """This method is designed to remove smartcoin to the user.

        Args:
            amount (int, optional): Number of smartcoin to remove. Defaults to 1.

        Raises:
            NotEnougtSmartcoinException: Raise when the user don't have enougt smartcoin.
        """
        if self.get_smartcoin() - amount < 0:
            raise NotEnougtSmartcoinException
        self.__db_access.remove_smartcoin(self.__discord_id, amount)
    
    def name_color(self) -> str:
        """This method is designed to get the name color of the user.

        Returns:
            str: The name color of the user as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
        return self.__db_access.get_user_profile_custom_color(self.__discord_id, ProfileColoredPart.NameColor)
    
    def bar_color(self) -> str:
        """This method is designed to get the bar color of the user.

        Returns:
            str: The bar color of the user as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
        return self.__db_access.get_user_profile_custom_color(self.__discord_id, ProfileColoredPart.BarColor)
    
    def is_root(self) -> bool:
        """This method is designed to check if the user is root.

        Returns:
            bool: True if the user is root, False if not.
        """
        return self.__db_access.get_if_user_is_root(self.__discord_id)
    
    def toggle_root(self, root: bool | None = None) -> None:
        """This method is designed to toggle the root of the user.

        Args:
            root (bool | None, optional): if bool set the bool if none toggle. Defaults to None.
        """
        if root is None:
            root = not self.is_root()
        self.__db_access.set_user_root(self.__discord_id, root)
    
    def current_wallpaper(self) -> Wallpaper:
        """This method is designed to get the current wallpaper of the user.

        Returns:
            Wallpaper: The current wallpaper of the user.
        """
        return Wallpaper(self.__db_access.get_user_current_wallpaper(self.__discord_id))
    
    def list_of_posseded_wallpapers(self) -> list[Wallpaper]: 
        """This method is designed to get the list of posseded wallpapers of the user.

        Returns:
            list[Wallpaper]: The list of posseded wallpapers of the user.
        """        
        return Wallpapers().create_list_wallpaper_by_list_name(self.__db_access.get_list_posseded_wallpapers(self.__discord_id)) 
    
    def change_current_wallpapers(self, wallpaper: Wallpaper) -> None:
        """This method is designed to change the current wallpaper of the user.

        Args:
            wallpaper (Wallpaper): The new current wallpaper of the user.

        Raises:
            WallpaperNotPossededException: Raise when the user don't possed the wallpaper.
        """
        if self.__is_wallpaper_posseded(wallpaper):
            self.__db_access.change_user_current_wallpaper(self.__discord_id, wallpaper.name())
        else:
            raise WallpaperNotPossededException
    
    def change_name_color(self, color: str) -> None:
        """This method is designed to change the name color of the user.

        Color list:
            - blue - 0000FF
            - white - FFFFFF
            - black - 000000
            - green - 00FF00
            - yellow - E6E600
            - pink - FF00FF
            - red - FF0000
            - orange - FF9900
            - purple - 990099
            - brown - D2691E
            - grey - 808080

        Args:
            color (str): The new color as Hex RGB or color name (example: 00ff00, ff00ffaf, red, orange, etc..).
        """
        self.__db_access.change_user_profile_custom_color(self.__discord_id, ProfileColoredPart.NameColor, Utils().check_color(color))

    def change_bar_color(self, color: str) -> None:
        """This method is designed to change the bar color of the user.

        Args:
            color (str): The new color as Hex RGB or color name (example: 00ff00, ff00ffaf, red, orange, etc..).
        """        
        self.__db_access.change_user_profile_custom_color(self.__discord_id, ProfileColoredPart.BarColor, Utils().check_color(color))

    def badges_list(self) -> list[str]:
        """This method is designed to get the badges list of the user.

        Returns:
            list[str]: The user badges list (example: ['badge_name', 'badge_name']).
        """
        return Badges().create_list_badges_by_list_name(self.__db_access.get_users_badge_list(self.__discord_id))
    
    def get_smartcoin(self) -> int:
        """This method is designed to get the smartcoin of the user.

        Returns:
            int: The smartcoin of the user.
        """
        return self.__db_access.get_smartcoin(self.__discord_id)
    
    def add_posseded_wallpaper(self, wallpaper: Wallpaper) -> None:
        """This method is designed to add a posseded wallpaper to the user.

        Args:
            wallpaper (Wallpaper): The wallpaper to add.

        Raises:
            WallpaperAlreadyPossededException: Raise when the user already possed the wallpaper.
        """
        if self.__is_wallpaper_posseded(wallpaper):
            raise WallpaperAlreadyPossededException
        self.__db_access.add_posseded_wallpaper(self.__discord_id, wallpaper.name())
    
    def buy_wallpaper(self, wallpaper: Wallpaper) -> None:
        """This method is designed to handle a buy of wallpaper by user.

        Args:
            wallpaper (Wallpaper): The wallpaper to buy.

        Raises:
            WallpaperAlreadyPossededException: Raise when the user already possed the wallpaper.
            WallpaperCannotBeBuyedException: Raise when the wallpaper cannot be buyed.
            NotEnougtSmartcoinException: Raise when the user don't have enougt smartcoin.
        """
        if self.__is_wallpaper_posseded(wallpaper):
            raise WallpaperAlreadyPossededException
        wallpaper_price = wallpaper.price()
        if wallpaper_price == 0:
            raise WallpaperCannotBeBuyedException
        if self.get_smartcoin() < wallpaper_price:
            raise NotEnougtSmartcoinException
        self.remove_smartcoin(wallpaper_price)
        self.add_posseded_wallpaper(wallpaper)
        
    def increase_number_of_buy(self) -> None:
        """This method is designed to increase the number of buy of the user.
        """
        self.__db_access.increase_number_of_buy(self.__discord_id)

    def __is_wallpaper_posseded(self, wallpaper: Wallpaper) -> bool:
        """This method is designed to check if a wallpaper is posseded by the user.

        Args:
            wallpaper (Wallpaper): The wallpaper to check.

        Returns:
            str: True if the user possed the wallpaper, False if not.
        """
        for posseded_wallpaper in self.list_of_posseded_wallpapers():
            if posseded_wallpaper.name() == wallpaper.name():
                return True
        return False

    def __check_add_level_up(self) -> None:
        """This method is designed to check if the user can level up.
        """
        point = self.point()
        level = self.level()
        calculated_point_per_level = 200 * level
        calculated_money_per_level = 100+(level*100)
        if level > 15:
            calculated_point_per_level = 200 * 15
            calculated_money_per_level = 100+(15*100)
        
        if point >= calculated_point_per_level:
            self.__db_access.add_user_level(self.__discord_id)
            self.__db_access.reset_point(self.__discord_id)
            self.__db_access.add_user_point(self.__discord_id, point - (calculated_point_per_level))
            self.add_smartcoin(calculated_money_per_level)
            self.__check_add_if_wallpaper_at_this_level()
    
    def __check_add_if_wallpaper_at_this_level(self) -> None:
        """This method is designed to check if the user can add a wallpaper at this level.
        """
        for wallpaper in Wallpapers().all():
            if wallpaper.level() == self.level():
                try:
                    self.add_posseded_wallpaper(wallpaper)
                except:
                    pass
                