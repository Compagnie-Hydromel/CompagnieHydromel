from enum import Enum

class ProfileColoredPart(Enum):
    BarColor = "barColor"
    NameColor = "nameColor"

class DatabaseAccessImplement:    
    def __init__(self) -> None:
        pass

    # Public 

    def get_user_level(self, discord_id: str) -> int:
        pass

    def get_user_point(self, discord_id: str) -> int:
        pass
    
    def get_smartcoin(self, discord_id: str) -> int:
        pass
    
    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        pass

    def add_user_level(self, discord_id: str, level = 1) -> None:
        pass

    def add_smartcoin(self, discord_id, amount=1) -> None:
        pass

    def remove_smartcoin(self, discord_id, amount=1) -> bool:
        pass

    def add_user_if_not_exist(self, discord_id: str) -> None:
        pass

    def reset_point(self, discord_id: str) -> None:
        pass

    def get_user_profile_color_bar(self, discord_id: str) -> str:
        pass

    def get_user_profile_color_name(self, discord_id: str) -> str:
        pass

    def get_if_user_is_root(self, discord_id: str) -> bool:
        pass

    def get_user_current_wallpaper(self, discord_id: str) -> str:
        pass

    def get_list_posseded_wallpapers(self, discord_id: str) -> list:
        pass

    def change_user_current_wallpaper(self, discord_id: str, wallpaper_name: str) -> None:
        pass

    def get_all_wallpapers(self) -> list:
        pass

    def is_wallpaper_exist(self, wallpaper_name: str) -> bool:
        pass

    def change_user_profile_custom_color(self, discord_id: str, profile_colored_part: ProfileColoredPart, color: str) -> None:
        pass
    
    def get_users_badge_list(self, discord_id: str) -> list:
        pass
    
    def get_top_users(self) -> list:
        pass

    def add_posseded_wallpaper(self, discordId: str, wallpaper_name: str) -> None:
        pass

    # Public