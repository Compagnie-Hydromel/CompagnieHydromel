class DatabaseAccessImplement:    
    def __init__(self) -> None:
        pass

    # Public 

    def get_user_level(self, discord_id: str) -> int:
        pass

    def get_user_point(self, discord_id: str) -> int:
        pass
    
    def get_balance(self, discord_id: str) -> int:
        pass
    
    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        pass

    def add_user_level(self, discord_id: str, level = 1) -> None:
        pass

    def add_balance(self, discord_id, amount=1) -> None:
        pass

    def remove_balance(self, discord_id, amount=1) -> bool:
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

    # Public