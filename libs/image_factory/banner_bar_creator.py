from io import BytesIO
from PIL import Image
from libs.exception.image.image_not_downloadable import ImageNotDownloadable
from libs.image_factory.utils import Utils as ImageFactoryUtils
from libs.storages.storage import Storage


class BannerBarCreator:
    """This class is designed to make a banner bar.    
    """
    __file_path: str

    def __init__(self, file_path: str, banner_image_url: str, coords: list[dict[str, int]], people: dict[int, list[dict[str, str]]]) -> None:
        """This method is designed to initialize the BannerBarCreator class and make the banner bar.

        coords = [
            {"x":390,"y":215, "id": 1131446231160328212},
            {"x":110,"y":279, "id": 1131446228916387900},
            {"x":607,"y":293, "id": 1131446229738467410},
            {"x":450,"y":457, "id": 1131446231160328212}
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
            banner_image_url (str): The banner image path.
            coords (list[dict[str, int]]): The coordinates of the people.
            people (dict[int, list[dict[str, str]]]): The people to add to the banner bar.

        Raises:
            ImageNotDownloadable: If the banner_image can't be downloaded.
        """
        self.storage = Storage()
        self.__file_path = file_path

        img = None
        try:
            img = Image.open(self.storage.get(
                banner_image_url, return_type=BytesIO)).convert('RGBA')
        except:
            raise ImageNotDownloadable()

        # image
        for channel in people:
            add = 0
            for member in people[channel]:
                try:
                    pic = Image.open(self.storage.get(member["profil"], return_type=BytesIO)).convert(
                        'RGBA').resize((64, 64))
                except:
                    raise ImageNotDownloadable()

                h, w = pic.size

                pic = ImageFactoryUtils.pillow_crop_max_square(
                    pic).resize((w, h), Image.LANCZOS)
                pic = ImageFactoryUtils.pillow_mask_circle_transparent(pic, 1)

                channel_found = self.__search_in_coords(coords, channel)

                if channel_found is None:
                    continue

                img.paste(
                    pic, (channel_found['x']+add, channel_found['y']), pic)
                add += int(64/(len(people[channel])/3))
        # image

        output = BytesIO()
        img.save(output, format='PNG')
        self.storage.put(output, self.file_path)

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
