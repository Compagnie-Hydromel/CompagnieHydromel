from PIL import Image
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException
from libs.image_factory.utils import Utils as ImageFactoryUtils
from libs.utils.utils import Utils

from libs.log import Log


class BannerBarCreator:
    """This class is designed to make a banner bar.    
    """
    __file_path: str

    def __init__(self, file_path: str, banner_image: str, coords: list[dict[str, int]], people: dict[int, list[dict[str, str]]]) -> None:
        """This method is designed to initialize the BannerBarCreator class and make the banner bar.

        coords = [
            {"w":390,"h":215, "id": 1131446231160328212},
            {"w":110,"h":279, "id": 1131446228916387900},
            {"w":607,"h":293, "id": 1131446229738467410},
            {"w":450,"h":457, "id": 1131446231160328212}
        ]

        people = {
            1131446231160328212: [
                {"username": "People 1", "profil": "https://discord.com/path/to/profile/picture" }
            ],
            1131446231160328212: [
                ...
            ],
            ...
        }

        Args:
            file_path (str): The file path to save the banner bar.
            banner_image (str): The banner image path.
            coords (list[dict[str, int]]): The coordinates of the people.
            people (dict[int, list[dict[str, str]]]): The people to add to the banner bar.

        Raises:
            UnableToDownloadImageException: If the banner_image can't be downloaded.
        """
        img = None
        try:
            img = Image.open(Utils.download_image(
                banner_image)).convert('RGBA')
        except:
            raise WallpaperIsNotDownloadableException

        # image
        for channel in people:
            add = 0
            for member in people[channel]:
                try:
                    pic = Image.open(Utils.download_image(
                        member["profil"])).convert('RGBA').resize((64, 64))
                except:
                    raise WallpaperIsNotDownloadableException

                h, w = pic.size

                pic = ImageFactoryUtils.pillow_crop_max_square(
                    pic).resize((w, h), Image.LANCZOS)
                pic = ImageFactoryUtils.pillow_mask_circle_transparent(pic, 1)

                channel_found = self.__search_in_coords(coords, channel)

                if channel_found is None:
                    continue

                img.paste(
                    pic, (channel_found['w']+add, channel_found['h']), pic)
                Log.info("BannerBarCreator: Added " +
                         member["username"] + " to the banner bar.")
                add += int(64/(len(people[channel])/3))
        # image

        img.save(file_path)
        self.__file_path = file_path

    @property
    def file_path(self) -> str:
        """This method is a getter to get the saved banner bar file path.

        Returns:
            str: The file path.
        """
        return self.__file_path

    def __search_in_coords(self, coords: list[dict[str, int]], channel: int) -> dict[str, int] | None:
        """This method is designed to search in the coords list.

        Args:
            coords (list[dict[str, int]]): The coords list.
            channel (int): The channel to search.

        Returns:
            dict[str, int]: The found channel.
            None: If the channel is not found.
        """
        for coord in coords:
            if coord['id'] == channel:
                return coord
        return None
