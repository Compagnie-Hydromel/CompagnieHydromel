from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers


class Utils:
    @staticmethod
    def add_test_wallpaper(name: str):
        wallpapers = Wallpapers()
        try:
            wallpapers.add(name, "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png", 10, 5)
        except:
            wallpapers.remove(Wallpaper(name))
            wallpapers.add(name, "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png", 10, 5)
            
    @staticmethod
    def wallpaper_in_list_of_wallpaper(wallpaper_name: str, list_of_wallpaper: list[Wallpaper]) -> bool:
        list_of_wallpaper_name = []
        for wallpaper_in_for in list_of_wallpaper:
            list_of_wallpaper_name.append(wallpaper_in_for.name())
        return wallpaper_name in list_of_wallpaper_name