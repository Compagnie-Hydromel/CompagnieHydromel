from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError, ImageFilter, ImageColor
from utils import pillow_crop_center, pillow_crop_max_square, pillow_mask_circle_transparent, pillow_new_bar
import requests
from io import BytesIO

class BannerBarCreator:
    __file_path: str 
    
    def __init__(self,file_path:str , wallpaper: str, coords: dict(str, int), people):
        img = Image.open(wallpaper).convert('RGBA')

        # image
        for server in people:
            add = 0
            for member in people[server]:
                response = requests.get(member["profil"])
                pic = Image.open(BytesIO(response.content)).convert('RGBA').resize((64,64))

                h,w = pic.size

                pic = pillow_crop_max_square(pic).resize((w, h), Image.LANCZOS)
                pic = pillow_mask_circle_transparent(pic, 1)

                img.paste(pic, (coords[server]['w']+add, coords[server]['h']), pic)
                add+=int(64/(len(people[server])/3))
        # image

        img.save(filePath)
        self.__file_path
    
    @property
    def file