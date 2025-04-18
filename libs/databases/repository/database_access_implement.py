from enum import Enum

from libs.databases.dto.layout import Layout


class ProfileColoredPart(Enum):
    BarColor = "barColor"
    NameColor = "nameColor"


class DatabaseAccessImplement:
    """This class is designed to be the interface of the database access.
    """

    def __init__(self) -> None:
        """This method is designed to initialize the class. Use it to initialize the database connection.
        """
        pass

    # Public

    def get_all_users(self) -> list[str]:
        """This method is designed to get all users.

        Returns:
            list[str]: All users discordId.
        """
        pass

    def get_most_smart_users(self) -> list[str]:
        """This method is designed to get the most smart users.

        Returns:
            list[str]: The most smart users list.
        """
        pass

    def get_user_level(self, discord_id: str) -> int:
        """This method is designed to get a user level number.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user level number.
        """
        pass

    def get_user_point(self, discord_id: str) -> int:
        """This method is designed to get a user number of point.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of point.
        """
        pass

    def get_smartpoint(self, discord_id: str) -> int:
        """This method is designed to get a user number of smartpoint.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of smartpoint.
        """
        pass

    def get_number_of_buy(self, discord_id: str) -> int:
        """This method is designed to get a user number of buy.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of buy.
        """
        pass

    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to add point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to add. Defaults to 1.
        """
        pass

    def add_user_level(self, discord_id: str, level=1) -> None:
        """This method is designed to add level to a user.

        Args:
            discord_id (str): Discord user id as a string.
            level (int, optional): The number of level to add. Defaults to 1.
        """
        pass

    def add_smartpoint(self, discord_id, amount=1) -> None:
        """This method is designed to add smartpoint to a user.

        Args:
            discord_id (_type_): Discord user id as a string.
            amount (int, optional): The number of smartpoint to add. Defaults to 1.
        """
        pass

    def remove_smartpoint(self, discord_id, amount=1) -> None:
        """This method is designed to remove smartpoint to a user.

        Args:
            discord_id (_type_): Discord user id as a string.
            amount (int, optional): The number of smartpoint to remove. Defaults to 1.
        """
        pass

    def add_user_monthly_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to add monthly point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to add. Defaults to 1.
        """
        pass

    def remove_user_monthly_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to remove monthly point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to remove. Defaults to 1.
        """
        pass

    def get_user_monthly_point(self, discord_id: str) -> int:
        """This method is designed to get a user number of monthly point.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of monthly point.
        """
        pass

    def reset_user_monthly_point(self, discord_id: str) -> None:
        """This method is designed to reset monthly point to 0.

        Args:
            discord_id (str): Discord user id as a string.
        """
        pass

    def add_user_if_not_exist(self, discord_id: str) -> None:
        """This method is designed to add a user if he doesn't exist.

        Args:
            discord_id (str): Discord user id as a string.
        """
        pass

    def reset_point(self, discord_id: str) -> None:
        """This method is designed to reset a user point to 0.

        Args:
            discord_id (str): Discord user id as a string.
        """
        pass

    def reset_level(self, discord_id: str) -> None:
        """This method is designed to reset a user level to 1.

        Args:
            discord_id (str): Discord user id as a string.
        """
        pass

    def get_user_profile_custom_color(self, discord_id: str, profile_colored_part: ProfileColoredPart) -> str:
        """This method is designed to get a user profile custom color.

        Args:
            discord_id (str): Discord user id as a string.
            profile_colored_part (ProfileColoredPart): The profile colored part (NameColor or BarColor).

        Returns:
            str: The user custom bar color as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
        pass

    def get_if_user_is_root(self, discord_id: str) -> bool:
        """This method is designed to get if a user is root.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            bool: True if the user is root, False if not.
        """
        pass

    def set_user_root(self, discord_id: str, is_root: bool) -> None:
        """This method is designed to set a user root.

        Args:
            discord_id (str): Discord user id as a string.
            is_root (bool): True if the user is root, False if not.
        """
        pass

    def get_user_current_wallpaper(self, discord_id: str) -> str:
        """This method is designed to get a user current wallpaper name.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            str: The user current wallpaper name. Return "default" if the user has a deleted wallpaper put on.
        """
        pass

    def get_list_posseded_wallpapers(self, discord_id: str) -> list[str]:
        """This method is designed to get a user posseded wallpapers list.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            list[str]: The user posseded wallpapers name list (example: ['default', 'wallpaper_name']).
        """
        pass

    def change_user_current_wallpaper(self, discord_id: str, wallpaper_name: str) -> None:
        """This method is designed to change a user current wallpaper.

        Args:
            discord_id (str): Discord user id as a string.
            wallpaper_name (str): The new wallpaper name.
        """
        pass

    def get_all_wallpapers(self) -> list[str]:
        """This method is designed to get all wallpapers name.

        Returns:
            list[str]: All wallpapers name (example: ['default', 'wallpaper_name']).
        """
        pass

    def is_wallpaper_exist(self, wallpaper_name: str) -> bool:
        """This method is designed to check if a wallpaper exist.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            bool: True if the wallpaper exist, False if not.
        """
        pass

    def get_wallpaper_price(self, wallpaper_name: str) -> int:
        """This method is designed to get a wallpaper price.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            int: The wallpaper price.
        """
        pass

    def get_wallpaper_url(self, wallpaper_name: str) -> str:
        """This method is designed to get a wallpaper url.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            str: The wallpaper url (example: https://example.com/img.png).
        """
        pass

    def get_wallpaper_level(self, wallpaper_name: str) -> str:
        """This method is designed to get a wallpaper level.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            str: The wallpaper level.
        """
        pass

    def change_user_profile_custom_color(self, discord_id: str, profile_colored_part: ProfileColoredPart, color: str) -> None:
        """This method is designed to change a user profile custom color.

        Args:
            discord_id (str): Discord user id as a string.
            profile_colored_part (ProfileColoredPart): The profile colored part (NameColor or BarColor).
            color (str): The new color as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
        pass

    def get_users_badge_list(self, discord_id: str) -> list[list[str]]:
        """This method is designed to get a user badge list.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            list[list[str]]: The user badge list (example: [['badge_name', 'https://badge_url'], ['badge_name', 'https://badge_url']]).
        """
        pass

    def get_top_users(self) -> list[str]:
        """This method is designed to get the top users.

        Returns:
            list[str]: The top users list (example: ['discord_id', 'discord_id']).
        """
        pass

    def get_root_users(self) -> list[str]:
        """This method is designed to get the root users.

        Returns:
            list[str]: The root users list (example: ['discord_id', 'discord_id']).
        """
        pass

    def add_posseded_wallpaper(self, discordId: str, wallpaper_name: str) -> None:
        """This method is designed to add a wallpaper to a user's possession.

        Args:
            discordId (str): Discord user id as a string.
            wallpaper_name (str): The wallpaper name.
        """
        pass

    def is_badge_exist(self, badge_name: str) -> bool:
        """This method is designed to check if a badge exist.

        Args:
            badge_name (str): The badge name.

        Returns:
            bool: True if the badge exist, False if not.
        """
        pass

    def get_badge_url(self, badge_name: str) -> str:
        """This method is designed to get a badge url.

        Args:
            badge_name (str): The badge name.

        Returns:
            str: The badge url (example: https://example.com/img.png).
        """
        pass

    def increase_number_of_buy(self, discord_id: str) -> None:
        """This method is designed to increase the number of buy of a user.

        Args:
            discord_id (str): Discord user id as a string.
        """
        pass

    def reset_number_of_buy(self, discord_id: str) -> None:
        """This method is designed to reset the number of buy of a user.

        Args:
            discord_id (str): Discord user id as a string.
        """
        pass

    def get_user_profile_layout(self, discord_id: str) -> dict[str, dict[str, int]]:
        """This method is designed to get user profile layout.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            dict[dict[str, int]]: The users profiles coords list (example: {"profilPicture": {"x": 0, "y": 0}, "name": ...}).
        """
        pass

    def change_user_profile_layout(self, discord_id: str, layout_name: str) -> None:
        """This method is designed to set user profile layout.

        Args:
            discord_id (str): Discord user id as a string.
            layout_name (str): The layout name.
        """
        pass

    def is_profile_layout_exist(self, layout_name: str) -> bool:
        """This method is designed to check if a profile layout exist.

        Args:
            layout_name (str): The layout name.

        Returns:
            bool: True if the user profile layout exist, False if not.
        """
        pass

    def get_all_profile_layouts_name(self) -> list[str]:
        """This method is designed to list all user profile layout name.

        Returns:
            list[str]: The list of all user profile layout name.
        """
        pass

    def get_profile_layout(self, layout_name: str) -> Layout:
        """This method is designed to get a profile layout.

        Args:
            layout_name (str): The layout name.

        Returns:
            Layout: The profile layout.
        """
        pass

    def get_default_profile_layout_name(self) -> str:
        """This method is designed to get the default profile layout name.

        Returns:
            str: The default profile layout name.
        """
        pass

    def add_profile_layout(self, layout_name: str, layout: Layout) -> None:
        """This method is designed to add a profile layout.

        Args:
            layout_name (str): The layout name.
            layout (Layout): The profile layout.
        """
        pass

    def remove_profile_layout(self, layout_name: str) -> None:
        """This method is designed to remove a profile layout.

        Args:
            layout_name (str): The layout name.
        """
        pass

    def update_profile_layout(self, layout_name: str, layout: Layout) -> None:
        """This method is designed to update a profile layout.

        Args:
            layout_name (str): The layout name.
            layout (Layout): The profile layout.
        """
        pass

    def rename_profile_layout(self, old_layout_name: str, new_layout_name: str) -> None:
        """This method is designed to rename a profile layout.

        Args:
            old_layout_name (str): The old layout name.
            new_layout_name (str): The new layout name.
        """
        pass

    def add_wallpaper(self, wallpaper_name: str, url: str, price: int, level: int) -> None:
        """This method is designed to add a wallpaper to the database.

        Args:
            wallpaper_name (str): The wallpaper name.
            url (str): The url of the wallpaper.
            price (int): The price of the wallpaper.
            level (int): The level of the wallpaper.
        """
        pass

    def remove_wallpaper(self, wallpaper_name: str) -> None:
        """This method is designed to remove a wallpaper from the database.

        Args:
            wallpaper_name (str): The wallpaper name.
        """
        pass

    def set_wallpaper_url(self, wallpaper_name: str, url: str) -> None:
        """This method is designed to set a wallpaper url.

        Args:
            wallpaper_name (str): The wallpaper name.
            url (str): The new url of the wallpaper.
        """
        pass

    def set_wallpaper_price(self, wallpaper_name: str, price: int) -> None:
        """This method is designed to set a wallpaper price.

        Args:
            wallpaper_name (str): The wallpaper name.
            price (int): The new price of the wallpaper.
        """
        pass

    def set_wallpaper_level(self, wallpaper_name: str, level: int) -> None:
        """This method is designed to set a wallpaper level.

        Args:
            wallpaper_name (str): The wallpaper name.
            level (int): The new level of the wallpaper.
        """
        pass

    def rename_wallpaper(self, old_wallpaper_name: str, new_wallpaper_name: str) -> None:
        """This method is designed to rename a wallpaper.

        Args:
            old_wallpaper_name (str): The old wallpaper name.
            new_wallpaper_name (str): The new wallpaper name.
        """
        pass

    def get_default_wallpaper_name(self) -> str:
        """This method is designed to get the default wallpaper name.

        Returns:
            str: The default wallpaper name.
        """
        pass

    def get_all_roles(self) -> list[str]:
        """This method is designed to get all roles.

        Returns:
            list[str]: All roles discordId.
        """
        pass

    def get_role_discord_id_by_role_level(self, level: int) -> str:
        """This method is designed to get a role discordId by role level.

        Args:
            level (int): The role level.

        Returns:
            str: The role discordId.
        """
        pass

    def is_role_exist(self, role_discord_id: str) -> bool:
        """This method is designed to check if a role exist.

        Args:
            role_discord_id (str): The role discordId.

        Returns:
            bool: True if the role exist, False if not.
        """
        pass

    def is_role_exist_by_level(self, role_level: int) -> bool:
        """This method is designed to check if a role exist.

        Args:
            role_level (int): The role of the role.

        Returns:
            bool: True if the role exist, False if not.
        """
        pass

    def get_role_level(self, role_discord_id: str) -> int:
        """This method is designed to get a level which the user need to get the role.

        Args:
            role_discord_id (str): The role discordId.

        Returns:
            int: The role level.
        """
        pass

    def add_role(self, role_discord_id: str, level: int) -> None:
        """This method is designed to add a role.

        Args:
            role_discord_id (str): The role discordId.
            level (int): The role level.
        """
        pass

    def remove_role(self, role_discord_id: str) -> None:
        """This method is designed to remove a role.

        Args:
            role_discord_id (str): The role discordId.
        """
        pass

    def update_role_level(self, role_discord_id: str, level: int) -> None:
        """This method is designed to update a role level.

        Args:
            role_discord_id (str): The role discordId.
            level (int): The new role level.
        """
        pass

    def is_user_accepted_rules(self, discord_id: str) -> bool:
        """This method is designed to check if a user accepted the rules.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            bool: True if the user accepted the rules, False if not.
        """
        pass

    def set_user_accepted_rules(self, discord_id: str, accepted: bool) -> None:
        """This method is designed to set a user accepted the rules.

        Args:
            discord_id (str): Discord user id as a string.
            accepted (bool): True if the user accepted the rules, False if not.
        """
        pass

    def get_5_monthly_most_active_users(self) -> list[str]:
        """This method is designed to get the 5 monthly most active users.

        Returns:
            list[str]: The 5 monthly most active users list.
        """
        pass

    # Public
