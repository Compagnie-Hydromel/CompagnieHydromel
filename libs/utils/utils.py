from io import BytesIO
import os
import random
import discord
import requests
import re

from libs.exception.color.color_not_correct_exception import ColorNotCorrectException
from libs.log import Log

class Utils():
    """This class is designed to manage the utils.
    """
    @staticmethod
    def createDirectoryIfNotExist(directory:str):
        """This method is designed to create a directory if not exist.

        Args:
            directory (str): The directory to create. (example: "path/to/directory")
        """
        if not os.path.exists(directory):
            Log.info("Creating directory " + directory)
            os.mkdir(directory)
    
    @staticmethod
    def download_image_with_list_random(list_of_url: list[str]) -> BytesIO:
        """This method is designed to download an image with a list of url.

        Args:
            list_of_url (list[str]): The list of url.

        Returns:
            BytesIO: The image.
        """
        return Utils.download_image(random.choice(list_of_url))
    
    @staticmethod
    def random_file(path: str) -> str:
        """This method is designed to get a random file.

        Args:
            path (str): The path to get a random file.

        Returns:
            str: The random file.
        """
        return path + "/" + random.choice(os.listdir(path))
    
    @staticmethod
    def download_image(url: str) -> BytesIO:
        """This method is designed to download an image.

        Args:
            url (str): The url of the image.

        Returns:
            BytesIO: The image.
        """
        Log.info("Downloading image from " + url)
        response_url = requests.get(url)
        Log.info("Downloaded image from " + url)
        return BytesIO(response_url.content)
    
    @staticmethod
    def check_color(color: str) -> str:
        """This method is designed to check if a color is correct.
        
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
            color (str): The color to check as Hex RGB or color name (example: 00ff00, ff00ffaf, blue, white, etc..).

        Raises:
            ColorNotCorrectException: Raise when the color is not correct.

        Returns:
            str: The color as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
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
        
    @staticmethod
    def is_url_image(image_url):
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
        return False
    
    @staticmethod
    def get_user_by_discord_id(discord_id: str, bot: discord.Bot) -> discord.User | None:
        user_id = 0
        try:  # to avoid error if discord_id is not an convertible in int
            user_id = int(discord_id)
        except: 
            pass

        return bot.get_user(user_id)
    
    @staticmethod
    def get_user_name_or_id_by_discord_id(discord_id: str, bot: discord.Bot) -> str:
        discord_user: discord.User | None = Utils.get_user_by_discord_id(discord_id, bot)
        
        if discord_user is None:
            return discord_id
        else:
            return discord_user.name