from PIL import Image
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException
from libs.utils import Utils
import requests
from io import BytesIO

class BannerBarCreator:
    """This class is designed to make a banner bar.    
    """
    __file_path: str 
    
    def __init__(self, file_path:str, banner_image: str, coords: dict[str, int], people):
        """This method is designed to initialize the BannerBarCreator class and make the banner bar.
        
        coords = {
            'bar': {"w":390,"h":215, "id": 1131446227431587870},
            'table1': {"w":110,"h":279, "id": 1131446228916387900},
            'table2': {"w":607,"h":293, "id": 1131446229738467410},
            'table3': {"w":450,"h":457, "id": 1131446231160328212}
        }
        
        people = {
            'bar': [
                {"username": "People 1", "profil": "https://discord.com/path/to/profile/picture" }
            ],
            'table1': [
                ...
            ],
            ...
        }
        
        Raises:
            UnableToDownloadImageException: If the banner_image can't be downloaded.
        """
        img = None
        try: 
            response_banner_image = requests.get(banner_image)
            img = Image.open(BytesIO(response_banner_image.content)).convert('RGBA')
        except: 
            raise WallpaperIsNotDownloadableException

        # image
        for channel in people:
            add = 0
            for member in people[channel]:
                try: 
                    response_profile = requests.get(member["profil"])
                    pic = Image.open(BytesIO(response_profile.content)).convert('RGBA').resize((64,64))
                except: 
                    raise WallpaperIsNotDownloadableException

                h,w = pic.size

                pic = Utils().pillow_crop_max_square(pic).resize((w, h), Image.LANCZOS)
                pic = Utils().pillow_mask_circle_transparent(pic, 1)

                img.paste(pic, (coords[channel]['w']+add, coords[channel]['h']), pic)
                add+=int(64/(len(people[channel])/3))
        # image

        img.save(file_path)
        self.__file_path = file_path
    
    @property
    def file_path(self) -> str:
        """This method is a getter to get the file path.

        Returns:
            str: The file path.
        """
        return self.__file_path