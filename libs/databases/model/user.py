from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.badge import Badge
from libs.databases.repository.database_access_implement import DatabaseAccessImplement, ProfileColoredPart
from libs.databases.model.profile_layout import ProfileLayout
from libs.databases.model.wallpaper import Wallpaper
from libs.exception.smartpoint.not_enougt_smartpoint_exception import NotEnougtSmartpointException
from libs.exception.wallpaper.wallpaper_already_posseded_exception import WallpaperAlreadyPossededException
from libs.exception.wallpaper.wallpaper_cannot_be_buyed_exception import WallpaperCannotBeBuyedException
from libs.exception.wallpaper.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.utils.utils import Utils


class User:
    """This class is designed to manage a single user.
    """
    __discord_id: str
    __db_access: DatabaseAccessImplement

    def __init__(self, discord_id: str) -> None:
        """This method is designed to initialize the User class.

        Args:
            discord_id (str): The discord id of the user.
        """
        self.__discord_id = discord_id
        self.__db_access = DatabasesSelecter().databases
        self.__db_access.add_user_if_not_exist(discord_id)

    @staticmethod
    def get_top_users() -> list["User"]:
        """This method is designed to get the top users.

        Returns:
            list[User]: A list of User object.
        """
        return User.__create_list_of_users_by_list_user_name(DatabasesSelecter().databases.get_top_users())

    @staticmethod
    def get_most_smart_users() -> list["User"]:
        """This method is designed to get the most smart users.

        Returns:
            list[User]: A list of User object.
        """
        return User.__create_list_of_users_by_list_user_name(DatabasesSelecter().databases.get_most_smart_users())

    @staticmethod
    def get_root_users() -> list["User"]:
        """This method is designed to get the root users.

        Returns:
            list[User]: The list of root users.
        """
        return User.__create_list_of_users_by_list_user_name(DatabasesSelecter().databases.get_root_users())

    @staticmethod
    def get_5_monthly_most_active_users() -> list["User"]:
        """This method is designed to get the 5 monthly most active users.

        Returns:
            list[User]: A list of User object.
        """
        return User.__create_list_of_users_by_list_user_name(DatabasesSelecter().databases.get_5_monthly_most_active_users())

    @staticmethod
    def all() -> list["User"]:
        """This method is designed to get all the users.

        Returns:
            list[User]: A list of User object.
        """
        return User.__create_list_of_users_by_list_user_name(DatabasesSelecter().databases.get_all_users())

    @property
    def discord_id(self) -> str:
        """This method is designed to get the discord id of the user.

        Returns:
            str: The discord id of the user.
        """
        return self.__discord_id

    @property
    def level(self) -> int:
        """This method is designed to get the level of the user.

        Returns:
            int: The level of the user.
        """
        return self.__db_access.get_user_level(self.__discord_id)

    @property
    def point(self) -> int:
        """This method is designed to get the point of the user.

        Returns:
            int: The point of the user.
        """
        return self.__db_access.get_user_point(self.__discord_id)

    @property
    def monthly_point(self) -> int:
        """This method is designed to get the monthly point of the user.

        Returns:
            int: The monthly point of the user.
        """
        return self.__db_access.get_user_monthly_point(self.__discord_id)

    @property
    def number_of_buy(self) -> int:
        """This method is designed to get the number of buy of the user.

        Returns:
            int: The number of buy of the user.
        """
        return self.__db_access.get_number_of_buy(self.__discord_id)

    def add_point(self, point: int = 1) -> None:
        """This method is designed to add point to the user.

        Args:
            point (int, optional): Number of point to add. Defaults to 1.
        """
        self.__db_access.add_user_point(self.__discord_id, point)
        self.__check_add_level_up()

    def reset_point(self) -> None:
        """This method is designed to reset the point of the user.
        """
        self.__db_access.reset_point(self.__discord_id)

    def reset_level(self) -> None:
        """This method is designed to reset the level of the user. (WARNING essentially for test)
        """
        self.__db_access.reset_level(self.__discord_id)

    def reset_monthly_point(self) -> None:
        """This method is designed to reset the monthly point of the user.
        """
        self.__db_access.reset_user_monthly_point(self.__discord_id)

    def add_monthly_point(self, point: int = 1) -> None:
        """This method is designed to add monthly point to the user.

        Args:
            point (int, optional): Number of monthly point to add. Defaults to 1.
        """
        self.__db_access.add_user_monthly_point(self.__discord_id, point)

    def remove_monthly_point(self, point: int = 1) -> None:
        """This method is designed to remove monthly point to the user.

        Args:
            point (int, optional): Number of monthly point to remove. Defaults to 1.
        """
        self.__db_access.remove_user_monthly_point(self.__discord_id, point)

    def add_smartpoint(self, amount: int = 1) -> None:
        """This method is designed to add smartpoint to the user.

        Args:
            amount (int, optional): Number of smartpoint to add. Defaults to 1.
        """
        self.__db_access.add_smartpoint(self.__discord_id, amount)

    def remove_smartpoint(self, amount: int = 1) -> None:
        """This method is designed to remove smartpoint to the user.

        Args:
            amount (int, optional): Number of smartpoint to remove. Defaults to 1.

        Raises:
            NotEnougtSmartpointException: Raise when the user don't have enougt smartpoint.
        """
        if self.smartpoint - amount < 0:
            raise NotEnougtSmartpointException
        self.__db_access.remove_smartpoint(self.__discord_id, amount)

    @property
    def name_color(self) -> str:
        """This method is designed to get the name color of the user.

        Returns:
            str: The name color of the user as Hex RGB (example: #00ff00, #ff00ffaf, etc..).
        """
        return "#" + self.__db_access.get_user_profile_custom_color(self.__discord_id, ProfileColoredPart.NameColor)

    @property
    def bar_color(self) -> str:
        """This method is designed to get the bar color of the user.

        Returns:
            str: The bar color of the user as Hex RGB (example: #00ff00, #ff00ffaf, etc..).
        """
        return "#" + self.__db_access.get_user_profile_custom_color(self.__discord_id, ProfileColoredPart.BarColor)

    @property
    def is_root(self) -> bool:
        """This method is designed to check if the user is root.

        Returns:
            bool: True if the user is root, False if not.
        """
        return self.__db_access.get_if_user_is_root(self.__discord_id)

    @property
    def has_accepted_rules(self) -> bool:
        """This method is designed to check if the user has accepted the rules.

        Returns:
            bool: True if the user has accepted the rules, False if not.
        """
        return self.__db_access.is_user_accepted_rules(self.__discord_id)

    def toggle_root(self, root: bool | None = None) -> None:
        """This method is designed to toggle the root of the user.

        Args:
            root (bool | None, optional): if bool set the bool if none toggle. Defaults to None.
        """
        if root is None:
            root = not self.is_root
        self.__db_access.set_user_root(self.__discord_id, root)

    def toggle_accepted_rules(self, accepted_rules: bool | None = None) -> None:
        """This method is designed to toggle the accepted rules of the user.

        Args:
            accepted_rules (bool | None, optional): if bool set the bool if none toggle. Defaults to None.
        """
        if accepted_rules is None:
            accepted_rules = not self.has_accepted_rules
        self.__db_access.set_user_accepted_rules(
            self.__discord_id, accepted_rules)

    @property
    def current_wallpaper(self) -> Wallpaper:
        """This method is designed to get the current wallpaper of the user.

        Returns:
            Wallpaper: The current wallpaper of the user.
        """
        return Wallpaper(self.__db_access.get_user_current_wallpaper(self.__discord_id))

    @property
    def list_of_posseded_wallpapers(self) -> list[Wallpaper]:
        """This method is designed to get the list of posseded wallpapers of the user.

        Returns:
            list[Wallpaper]: The list of posseded wallpapers of the user.
        """
        return Wallpaper.create_list_wallpaper_by_list_name(self.__db_access.get_list_posseded_wallpapers(self.__discord_id))

    @property
    def profiles_layout(self) -> ProfileLayout:
        """This method is designed to get the profiles layout of the user.

        Raises:
            ProfileLayoutNotExist: Raise when the profile layout of the user don't exist.

        Returns:
            ProfileLayout: The users profiles layout.
        """
        return ProfileLayout(self.__db_access.get_user_profile_layout(self.__discord_id))

    def change_current_wallpapers(self, wallpaper: Wallpaper) -> None:
        """This method is designed to change the current wallpaper of the user.

        Args:
            wallpaper (Wallpaper): The new current wallpaper of the user.

        Raises:
            WallpaperNotPossededException: Raise when the user don't possed the wallpaper.
        """
        if self.__is_wallpaper_posseded(wallpaper):
            self.__db_access.change_user_current_wallpaper(
                self.__discord_id, wallpaper.name)
        else:
            raise WallpaperNotPossededException

    def change_name_color(self, color: str) -> None:
        """This method is designed to change the name color of the user.

        Color list:
            - blue - #0000FF
            - white - #FFFFFF
            - black - #000000
            - green - #00FF00
            - yellow - #E6E600
            - pink - #FF00FF
            - red - #FF0000
            - orange - #FF9900
            - purple - #990099
            - brown - #D2691E
            - grey - #808080

        Args:
            color (str): The new color as Hex RGB or color name (example: #00ff00, #ff00ffaf, red, orange, etc..).
        """
        self.__db_access.change_user_profile_custom_color(
            self.__discord_id, ProfileColoredPart.NameColor, Utils.check_color(color))

    def change_bar_color(self, color: str) -> None:
        """This method is designed to change the bar color of the user.

        Color list:
            - blue - #0000FF
            - white - #FFFFFF
            - black - #000000
            - green - #00FF00
            - yellow - #E6E600
            - pink - #FF00FF
            - red - #FF0000
            - orange - #FF9900
            - purple - #990099
            - brown - #D2691E
            - grey - #808080

        Args:
            color (str): The new color as Hex RGB or color name (example: #00ff00, #ff00ffaf, red, orange, etc..).
        """
        self.__db_access.change_user_profile_custom_color(
            self.__discord_id, ProfileColoredPart.BarColor, Utils.check_color(color))

    @property
    def badges_list(self) -> list[str]:
        """This method is designed to get the badges list of the user.

        Returns:
            list[str]: The user badges list (example: ['badge_name', 'badge_name']).
        """
        return Badge.create_list_badges_by_list_name(self.__db_access.get_users_badge_list(self.__discord_id))

    @property
    def smartpoint(self) -> int:
        """This method is designed to get the smartpoint of the user.

        Returns:
            int: The smartpoint of the user.
        """
        return self.__db_access.get_smartpoint(self.__discord_id)

    def add_posseded_wallpaper(self, wallpaper: Wallpaper) -> None:
        """This method is designed to add a posseded wallpaper to the user.

        Args:
            wallpaper (Wallpaper): The wallpaper to add.

        Raises:
            WallpaperAlreadyPossededException: Raise when the user already possed the wallpaper.
        """
        if self.__is_wallpaper_posseded(wallpaper):
            raise WallpaperAlreadyPossededException
        self.__db_access.add_posseded_wallpaper(
            self.__discord_id, wallpaper.name)

    def buy_wallpaper(self, wallpaper: Wallpaper) -> None:
        """This method is designed to handle a buy of wallpaper by user.

        Args:
            wallpaper (Wallpaper): The wallpaper to buy.

        Raises:
            WallpaperAlreadyPossededException: Raise when the user already possed the wallpaper.
            WallpaperCannotBeBuyedException: Raise when the wallpaper cannot be buyed.
            NotEnougtSmartpointException: Raise when the user don't have enougt smartpoint.
        """
        if self.__is_wallpaper_posseded(wallpaper):
            raise WallpaperAlreadyPossededException
        wallpaper_price = wallpaper.price
        if wallpaper_price == 0:
            raise WallpaperCannotBeBuyedException
        if self.smartpoint < wallpaper_price:
            raise NotEnougtSmartpointException
        self.remove_smartpoint(wallpaper_price)
        self.add_posseded_wallpaper(wallpaper)

    def increase_number_of_buy(self) -> None:
        """This method is designed to increase the number of buy of the user.
        """
        self.__db_access.increase_number_of_buy(self.__discord_id)

    def reset_number_of_buy(self) -> None:
        """This method is designed to reset the number of buy of the user.
        """
        self.__db_access.reset_number_of_buy(self.__discord_id)

    def change_profile_layout(self, profile_layout: ProfileLayout) -> None:
        """This method is designed to change the profile layout of the user.

        Args:
            profile_layout (ProfileLayout): The new profile layout of the user.
        """
        self.__db_access.change_user_profile_layout(
            self.__discord_id, profile_layout.name)

    def __is_wallpaper_posseded(self, wallpaper: Wallpaper) -> bool:
        """This method is designed to check if a wallpaper is posseded by the user.

        Args:
            wallpaper (Wallpaper): The wallpaper to check.

        Returns:
            str: True if the user possed the wallpaper, False if not.
        """
        for posseded_wallpaper in self.list_of_posseded_wallpapers:
            if posseded_wallpaper.name == wallpaper.name:
                return True
        return False

    def __check_add_level_up(self) -> None:
        """This method is designed to check if the user can level up.
        """
        point = self.point
        level = self.level
        calculated_point_per_level = 200 * level
        calculated_money_per_level = 100+(level*100)
        if level > 15:
            calculated_point_per_level = 200 * 15
            calculated_money_per_level = 100+(15*100)

        if point >= calculated_point_per_level:
            self.__db_access.add_user_level(self.__discord_id)
            self.reset_point()
            self.__db_access.add_user_point(
                self.__discord_id, point - (calculated_point_per_level))
            self.add_smartpoint(calculated_money_per_level)
            self.__check_add_if_wallpaper_at_this_level()

    def __check_add_if_wallpaper_at_this_level(self) -> None:
        """This method is designed to check if the user can add a wallpaper at this level.
        """
        for wallpaper in Wallpaper.all():
            if wallpaper.level == self.level:
                try:
                    self.add_posseded_wallpaper(wallpaper)
                except:
                    pass

    @staticmethod
    def __create_list_of_users_by_list_user_name(list_name: list[str]) -> list["User"]:
        """This method is designed to create a list of User object by a list of user name.

        Args:
            list_name (list[str]): A list of user name.

        Returns:
            list[User]: A list of User object.
        """
        list_of_users = []

        for user in list_name:
            list_of_users.append(User(user))

        return list_of_users
