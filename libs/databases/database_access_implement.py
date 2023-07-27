from enum import Enum

class ProfileColoredPart(Enum):
    BarColor = "barColor"
    NameColor = "nameColor"

class DatabaseAccessImplement:    
    def __init__(self) -> None:
        pass

    # Public 

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
    
    def get_smartcoin(self, discord_id: str) -> int:
        """This method is designed to get a user number of smartcoin.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of smartcoin.
        """
        pass
    
    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to add point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to add. Defaults to 1.
        """
        pass

    def add_user_level(self, discord_id: str, level = 1) -> None:
        """This method is designed to add level to a user.
        
        Args:
            discord_id (str): Discord user id as a string.
            level (int, optional): The number of level to add. Defaults to 1.
        """
        pass

    def add_smartcoin(self, discord_id, amount=1) -> None:
        """This method is designed to add smartcoin to a user.

        Args:
            discord_id (_type_): Discord user id as a string.
            amount (int, optional): The number of smartcoin to add. Defaults to 1.
        """
        pass

    def remove_smartcoin(self, discord_id, amount=1) -> None:
        """This method is designed to remove smartcoin to a user.

        Args:
            discord_id (_type_): Discord user id as a string.
            amount (int, optional): The number of smartcoin to remove. Defaults to 1.
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

    def get_user_current_wallpaper(self, discord_id: str) -> str:
        """This method is designed to get a user current wallpaper name.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            str: The user current wallpaper name.
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

    def add_posseded_wallpaper(self, discordId: str, wallpaper_name: str) -> None:
        """This method is designed to add a wallpaper to a user's possession.

        Args:
            discordId (str): Discord user id as a string.
            wallpaper_name (str): The wallpaper name.
        """
        pass

    # Public