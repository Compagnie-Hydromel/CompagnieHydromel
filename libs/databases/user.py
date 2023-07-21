import re
from libs.databases.database_access_implement import DatabaseAccessImplement, ProfileColoredPart
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.databases.wallpapers import Wallpapers
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.exception.not_enougt_smartcoin_exception import NotEnougtSmartcoinException
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper_not_posseded_exception import WallpaperNotPossededException

class User:
    __discord_id : str
    __db_access : DatabaseAccessImplement
    
    def __init__(self, discord_id : str) -> None:
        self.__discord_id = discord_id
        self.__db_access = SqliteAccess()
        self.__db_access.add_user_if_not_exist(discord_id)
    
    def discord_id(self) -> str:
        return self.__discord_id
    
    def level(self) -> int:
        return self.__db_access.get_user_level(self.__discord_id)

    def point(self) -> int:
        return self.__db_access.get_user_point(self.__discord_id)
    
    def add_point(self, point : int = 1) -> None:
        self.__db_access.add_user_point(self.__discord_id, point)
        self.__check_level_up()

    def add_smartcoin(self, amount : int = 1) -> None: 
        self.__db_access.add_smartcoin(self.__discord_id, amount)

    def remove_smartcoin(self, amount : int = 1) -> None:
        if not self.__db_access.remove_smartcoin(self.__discord_id, amount):
            raise NotEnougtSmartcoinException

    def name_color(self) -> str:
        return self.__db_access.get_user_profile_color_name(self.__discord_id)
    
    def bar_color(self) -> str:
        return self.__db_access.get_user_profile_color_bar(self.__discord_id)
    
    def is_root(self) -> bool:
        return self.__db_access.get_if_user_is_root(self.__discord_id)
    
    def current_wallpaper(self) -> str:
        return self.__db_access.get_user_current_wallpaper(self.__discord_id)
    
    def list_of_posseded_wallpapers(self) -> str:
        return self.__db_access.get_list_posseded_wallpapers(self.__discord_id)
    
    def change_current_wallpapers(self, wallpaper_name: str) -> None:
        if(Wallpapers().is_exist(wallpaper_name)):
            if self.__is_wallpaper_posseded(wallpaper_name):
                self.__db_access.change_user_current_wallpaper(self.__discord_id, wallpaper_name)
            else:
                raise WallpaperNotPossededException
        else:
            raise WallpaperNotExistException
    
    def change_name_color(self, color: str) -> None:
        self.__db_access.change_user_profile_custom_color(self.__discord_id, ProfileColoredPart.NameColor, self.__check_color(color))

    def change_bar_color(self, color: str) -> None:
        self.__db_access.change_user_profile_custom_color(self.__discord_id, ProfileColoredPart.BarColor, self.__check_color(color))

    def badge_list(self) -> list:
        return self.__db_access.get_users_badge_list(self.__discord_id)
    
    def get_smartcoin(self) -> int:
        return self.__db_access.get_smartcoin(self.__discord_id)

    def __check_color(self, color) -> str:
        hex_regex_check=re.findall(r'^#(?:[0-9a-fA-F]{3}){1,2}$|^#(?:[0-9a-fA-F]{3,4}){1,2}$',color)
    
        color_list = {
            "blue":"0000FF",
            "white":"FFFFFF",
            "black":"000000",
            "green":"00FF00",
            "yellow":"E6E600",
            "pink":"FF00FF",
            "red":"FF0000",
            "orange":"FF9900",
            "purple":"990099",
            "brown":"D2691E",
            "grey":"808080"
        }
        
        if hex_regex_check:
            return hex_regex_check[0].replace("#","")
        elif color in color_list:
            return color_list[color]
        else:
            raise ColorNotCorrectException

    def __is_wallpaper_posseded(self, wallpaper_name) -> str:
        for posseded_wallpaper in self.list_of_posseded_wallpapers():
            if posseded_wallpaper[0] == wallpaper_name:
                return True
        return False

    def __check_level_up(self) -> None:
        point = self.point()
        level = self.level()
        if point >= 200 * level:
            self.__db_access.add_user_level(self.__discord_id)
            self.__db_access.reset_point(self.__discord_id)
            self.__db_access.add_user_point(self.__discord_id, point - (200 * level))
            self.add_smartcoin(100+(level*100))