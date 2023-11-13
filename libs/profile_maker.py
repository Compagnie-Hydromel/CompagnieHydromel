#!/usr/local/bin/python3
from PIL import Image, ImageDraw, ImageFont, ImageColor
from libs.log import Log, LogType
from libs.utils import Utils
import requests
from io import BytesIO
from libs.databases.model.badge.badge import Badge
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException

class ProfilMaker():
    """This class is designed to make a profile.
    """
    __coords = {
        'profil_picture':{'x': 0,'y': 0},
        'name':{'x': 150,'y': 20},
        'username':{'x': 150,'y': 65},
        'level':{'x': 250,'y': 224},
        'badge':{'x': 150,'y': 90},
        'level_bar':{'x': 0,'y': 254}
    }

    def __init__(self,
                 profil_path: str,
                 user_name: str,
                 user_profil_picture: str,
                 level: int,
                 point: int,
                 display_name: str,
                 background_url: str,
                 coords: dict = __coords,
                 badges: list[Badge] = [],
                 name_color: str = "#0000FF",
                 bar_color: str = "#ADFF2F"
                 ):
        """This method is designed to initialize the ProfilMaker class and make the profile.
        
        Args:
            profil_path (str): Path to save the profile.
            user_name (str): Username show in the profile.
            user_profil_picture (str): Users profile picture url (https://discord.com/path/to/profil.png).
            level (int): Level show in the profile.
            point (int): Point show in the profile.
            display_name (str): Display name show in the profile.
            background_url (str): background url (https://example.com/path/to/background.png).
            coords (dict, optional): Coordonate to puts the different display object (name, profilPicture) see behind the paterns. Defaults to __coords.
            badge (list[badge], optional): The badge list in the profile (example: []). Defaults to [].
            name_color (str, optional): The color name as Hex RGB(example: 00ff00, ff00ffaf, etc..). Defaults to "#0000FF".
            bar_color (str, optional): The bar name as Hex RGB(example: 00ff00, ff00ffaf, etc..). Defaults to "#ADFF2F".
            
        __coords = {
            'profil_picture':{'x': 0,'y': 0},
            'name':{'x': 150,'y': 20},
            'username':{'x': 150,'y': 65},
            'level':{'x': 250,'y': 224},
            'badge':{'x': 150,'y': 90},
            'level_bar':{'x': 0,'y': 254}
        }

        Raises:
            UnableToDownloadImageException: If one of the image can't be downloaded.
        """
        
        # region [background]
        img = None
        try: 
            img = Image.open(Utils().download_image(background_url)).convert('RGBA').resize((500, 281))
        except Exception as e:
            Log(str(e), LogType.ERROR)
            raise WallpaperIsNotDownloadableException

        # endregion
        
        # region [bar and name color]
        _name_color = ImageColor.getcolor(str(name_color), "RGBA")
        _bar_color = ImageColor.getcolor(str(bar_color), "RGBA")
        # endregion

        # region [image]
        pic = None
        try: 
            response_profile_picture = requests.get(user_profil_picture)
            pic = Image.open(BytesIO(response_profile_picture.content)).convert(
                'RGBA').resize((128, 128))
        except Exception as e:
            Log(str(e), LogType.ERROR)
            raise WallpaperIsNotDownloadableException

        h, w = pic.size

        pic = Utils().pillow_crop_max_square(pic).resize((w, h), Image.Resampling.LANCZOS)
        pic = Utils().pillow_mask_circle_transparent(pic, 1)

        img.paste(pic, (coords["profil_picture"]['x'],
                  coords["profil_picture"]['y']), pic)
        # endregion

        # region [text]
        d = ImageDraw.Draw(img)
        # endregion

        # region [name]
        d.multiline_text((coords["name"]['x'], coords["name"]['y']), display_name, font=ImageFont.truetype(
            "data/font/ancientMedium.ttf", 45), fill=_name_color)

        d.multiline_text((coords["username"]['x'], coords["username"]['y']), user_name, font=ImageFont.truetype(
            "data/font/LiberationSans-Regular.ttf", 20), fill=_name_color)
        # endregion

        # region [level]
        d.multiline_text((coords["level"]['x'], coords["level"]['y']), str(
            level), font=ImageFont.truetype("data/font/LiberationSans-Regular.ttf", 30), fill=_bar_color)
        # endregion

        # region [badge]

        badgeNumber = 0
        for badge in badges:
            tempImg = None
            try:
                response_background_url = requests.get(badge.url)
                tempImg = Image.open(BytesIO(response_background_url.content)).convert('RGBA')
            except Exception as e:
                Log(str(e), LogType.ERROR)
                raise WallpaperIsNotDownloadableException
            tempImg.thumbnail((32, 32), Image.LANCZOS)
            img.paste(tempImg, (coords['badge']['x']+(34*badgeNumber), coords['badge']['y']), tempImg)
            badgeNumber += 1

        # endregion
        
        # region [level bar]
        calculated_point_per_level = 200 * level
        if level > 15:
            calculated_point_per_level = 200 * 15

        progress = (point * 100 / (calculated_point_per_level))/100

        bar = Utils().pillow_new_bar(1, 1, 500, 25, progress, fg=_bar_color)

        img.paste(bar, (coords['level_bar']['x'], coords['level_bar']['y']), bar)
        # endregion

        # region [save]
        img.save(profil_path)

        self.__profilPath = profil_path
        # endregion

    @property
    def profil_path(self) -> str:
        """This method is designed to get the profil path.

        Returns:
            str: The profil path.
        """
        return self.__profilPath