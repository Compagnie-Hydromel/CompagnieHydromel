from io import BytesIO
import os
import random
from PIL import Image, ImageDraw, ImageFilter
import requests

class Utils():
    """This class is designed to manage the utils.
    """
    def createDirectoryIfNotExist(self, directory:str):
        """This method is designed to create a directory if not exist.

        Args:
            directory (str): The directory to create. (example: "path/to/directory")
        """
        if not os.path.exists(directory):
            os.mkdir(directory)
    
    def __pillow_crop_center(self, pil_img: Image, crop_width: int, crop_height: int):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))

    def pillow_crop_max_square(self, pil_img: Image):
        return self.__pillow_crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def pillow_mask_circle_transparent(self, pil_img: Image, blur_radius: float, offset: int = 0):
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = pil_img.copy()
        result.putalpha(mask)

        return result

    def pillow_new_bar(self, x: int, y: int, width: int, height: int, progress: int, fg=(173, 255, 47, 255), fg2=(15, 15, 15, 0)):
        bar = Image.new(mode="RGBA", size=(width+(x*2)*2, height+(y*2)*2))
        draw = ImageDraw.Draw(bar)

        # Draw the background
        draw.rectangle((x+(height/2), y, x+width+(height/2),
                       y+height), fill=fg2, width=10)
        draw.ellipse((x+width, y, x+height+width, y+height), fill=fg2)
        draw.ellipse((x, y, x+height, y+height), fill=fg2)
        width = int(width*progress)

        # Draw the part of the progress bar that is actually filled
        draw.rectangle((x+(height/2), y, x+width+(height/2),
                       y+height), fill=fg, width=10)
        draw.ellipse((x+width, y, x+height+width, y+height), fill=fg)
        draw.ellipse((x, y, x+height, y+height), fill=fg)

        return bar
    
    def download_image_with_list_random(self, list_of_url: list[str]) -> BytesIO:
        """This method is designed to download an image with a list of url.

        Args:
            list_of_url (list[str]): The list of url.

        Returns:
            BytesIO: The image.
        """
        response_beers = requests.get(random.choice(list_of_url))
        return BytesIO(response_beers.content)
    
    def random_file(self, path: str) -> str:
        """This method is designed to get a random file.

        Args:
            path (str): The path to get a random file.

        Returns:
            str: The random file.
        """
        return path + "/" + random.choice(os.listdir(path))