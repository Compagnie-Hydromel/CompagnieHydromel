#!/usr/local/bin/python3
from PIL import Image, ImageDraw, ImageFont, ImageColor
from libs.exception.image.image_not_downloadable import ImageNotDownloadable
from libs.log import Log
from libs.image_factory.utils import Utils as ImageFactoryUtils
from libs.storages.storage import Storage
from io import BytesIO
from libs.databases.models.badge import Badge


class ProfilMaker():
    """This class is designed to make a profile.
    """
    __coords = {
        'profil_picture': {'x': 0, 'y': 0},
        'name': {'x': 150, 'y': 20},
        'username': {'x': 150, 'y': 65},
        'level': {'x': 250, 'y': 224},
        'badge': {'x': 150, 'y': 90},
        'level_bar': {'x': 0, 'y': 254}
    }

    def __init__(self,
                 profile_id: str,
                 user_name: str,
                 user_profil_picture: str,
                 level: int,
                 point: int,
                 display_name: str,
                 background_url: str | list[str],
                 coords: dict = __coords,
                 badges: list[Badge] = [],
                 name_color: str = "#0000FF",
                 bar_color: str = "#ADFF2F"
                 ):
        """This method is designed to initialize the ProfilMaker class and make the profile.

        Args:
            profile_id (str): The id of the profile.
            user_name (str): Username show in the profile.
            user_profil_picture (str): Users profile picture url (https://discord.com/path/to/profil.png).
            level (int): Level show in the profile.
            point (int): Point show in the profile.
            display_name (str): Display name show in the profile.
            background_url (str | list[str]): background url (https://example.com/path/to/background.png) or a list of background image.
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
        self.storage = Storage()

        # region [background]
        imgs: list[Image.Image] = []

        if isinstance(background_url, str):
            background_url = [background_url]
        elif not isinstance(background_url, list) or len(background_url) == 0:
            raise ImageNotDownloadable

        if len(background_url) == 1:
            url_extension = self.storage.get_file_type(
                background_url[0]).lower()

            try:
                if url_extension == "gif":
                    imgs = ImageFactoryUtils.gif_to_image_list(
                        self.storage.get(background_url[0], return_type=BytesIO))
                else:
                    for url in background_url:
                        imgs.append(Image.open(
                            self.storage.get(url, return_type=BytesIO)))
            except Exception as e:
                Log.error(str(e))
                raise ImageNotDownloadable

        # endregion

        self.__profilPath = "caches://profile/" + \
            str(profile_id) + (".gif" if len(imgs) > 1 else ".png")

        # region [bar and name color]
        _name_color = ImageColor.getcolor(name_color, "RGBA")
        _bar_color = ImageColor.getcolor(bar_color, "RGBA")
        # endregion

        image_to_appends = []

        profile_picture = None
        try:
            profile_picture = Image.open(self.storage.get(
                user_profil_picture, return_type=BytesIO)).convert('RGBA').resize((128, 128))
            profile_picture = ImageFactoryUtils.pillow_crop_max_square(
                profile_picture)
            profile_picture = ImageFactoryUtils.pillow_mask_circle_transparent(
                profile_picture, 1)
        except Exception as e:
            Log.error(str(e))
            raise ImageNotDownloadable

        badges_images = []
        for badge in badges:
            try:
                temp_img = Image.open(self.storage.get(
                    badge.url, return_type=BytesIO)).convert('RGBA')
                temp_img.thumbnail((32, 32), Image.LANCZOS)
                badges_images.append(temp_img)
            except Exception as e:
                Log.error(str(e))
                raise ImageNotDownloadable

        font_size = max(23, 40 - len(display_name) // 2)
        font_name = ImageFont.truetype(
            "assets/fonts/LiberationSans-Regular.ttf", font_size)
        font_username = ImageFont.truetype(
            "assets/fonts/LiberationSans-Regular.ttf", 20)
        font_level = ImageFont.truetype(
            "assets/fonts/LiberationSans-Regular.ttf", 30)

        calculated_point_per_level = min(200 * level, 200 * 15)
        progress = (point * 100 / calculated_point_per_level) / 100
        level_bar = ImageFactoryUtils.pillow_new_bar(
            1, 1, 500, 25, progress, fg=_bar_color)

        for x, img in enumerate(imgs):
            img = img.convert('RGBA').resize((500, 281))
            img.paste(profile_picture, (coords["profil_picture"]['x'],
                      coords["profil_picture"]['y']), profile_picture)

            d = ImageDraw.Draw(img)
            d.multiline_text((coords["name"]['x'], coords["name"]['y']),
                             display_name, font=font_name, fill=_name_color)
            d.multiline_text((coords["username"]['x'], coords["username"]
                             ['y']), user_name, font=font_username, fill=_name_color)
            d.multiline_text((coords["level"]['x'], coords["level"]['y']), str(
                level), font=font_level, fill=_bar_color)

            for i, badge_img in enumerate(badges_images):
                img.paste(
                    badge_img, (coords['badge']['x'] + (34 * i), coords['badge']['y']), badge_img)

            img.paste(
                level_bar, (coords['level_bar']['x'], coords['level_bar']['y']), level_bar)

            imgs[x] = img
            if x != 0:
                image_to_appends.append(img)

        # region [save]
        output = BytesIO()
        imgs[0].save(output, format="GIF" if image_to_appends else "PNG", append_images=image_to_appends,
                     save_all=True, duration=0, loop=0)
        self.storage.put(output, self.__profilPath)
        # endregion

    @property
    def profil_path(self) -> str:
        """This method is designed to get the saved profil path.

        Returns:
            str: The profil path.
        """
        return self.__profilPath
