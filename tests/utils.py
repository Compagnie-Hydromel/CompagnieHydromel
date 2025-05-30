import os
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.model.wallpaper import Wallpaper
from libs.databases.model.profile_layout import ProfileLayout


class Utils:
    @staticmethod
    def add_test_wallpaper(name: str):
        try:
            Wallpaper.create(
                name, "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png", 10, 5)
        except:
            Wallpaper.remove(Wallpaper(name))
            Wallpaper.create(
                name, "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png", 10, 5)

    @staticmethod
    def wallpaper_in_list_of_wallpaper(wallpaper_name: str, list_of_wallpaper: list[Wallpaper]) -> bool:
        list_of_wallpaper_name = []
        for wallpaper_in_for in list_of_wallpaper:
            list_of_wallpaper_name.append(wallpaper_in_for.name)
        return wallpaper_name in list_of_wallpaper_name

    @staticmethod
    def add_profile_layout(profile_layout_name: str) -> Layout:
        layout: Layout = Layout(
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
            Coords(0, 0),
        )
        ProfileLayout.add(profile_layout_name, layout)
        return layout

    @staticmethod
    def deleteFileIfExist(file: str):
        """This method is designed to delete a file if exist.

        Args:
            file (str): The file to delete. (example: "path/to/file")
        """
        if os.path.exists(file):
            os.remove(file)
