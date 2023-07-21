#!/usr/local/bin/python3
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError, ImageFilter, ImageColor
import requests
from io import BytesIO
import numpy as np
import os
from libs.exception.unable_to_download_wallpaper_exception import UnableToDownloadImageException

class ProfilMaker():
    __coords = {
        'profilPicture':{'x': 0,'y': 0},
        'name':{'x': 150,'y': 20},
        'userName':{'x': 150,'y': 65},
        'level':{'x': 250,'y': 224},
        'badge':{'x': 150,'y': 90},
        'levelBar':{'x': 0,'y': 254}
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
                 badge: list = [],
                 name_color: str = "#0000FF",
                 bar_color: str = "#ADFF2F"
                 ):
        img = None
        try:
            response_background_url = requests.get(background_url)
            img = Image.open(BytesIO(response_background_url.content)).convert('RGBA').resize((500, 281))
        except: 
            raise UnableToDownloadImageException

        _name_color = ImageColor.getcolor(str(name_color), "RGBA")
        _bar_color = ImageColor.getcolor(str(bar_color), "RGBA")

        # image
        pic = None
        try: 
            response_profile_picture = requests.get(user_profil_picture)
            pic = Image.open(BytesIO(response_profile_picture.content)).convert(
                'RGBA').resize((128, 128))
        except: 
            raise UnableToDownloadImageException

        h, w = pic.size

        pic = self.__crop_max_square(pic).resize((w, h), Image.Resampling.LANCZOS)
        pic = self.__mask_circle_transparent(pic, 1)

        img.paste(pic, (coords["profilPicture"]['x'],
                  coords["profilPicture"]['y']), pic)

        # text
        d = ImageDraw.Draw(img)

        # name
        d.multiline_text((coords["name"]['x'], coords["name"]['y']), display_name, font=ImageFont.truetype(
            "data/font/ancientMedium.ttf", 45), fill=_name_color)

        d.multiline_text((coords["userName"]['x'], coords["userName"]['y']), user_name, font=ImageFont.truetype(
            "data/font/LiberationSans-Regular.ttf", 20), fill=_name_color)

        # level
        d.multiline_text((coords["level"]['x'], coords["level"]['y']), str(
            level), font=ImageFont.truetype("data/font/LiberationSans-Regular.ttf", 30), fill=_bar_color)

        # badge

        badgeNumber = 0
        for i in badge:
            tempImg = None
            try:
                response_background_url = requests.get(i[1])
                tempImg = Image.open(BytesIO(response_background_url.content)).convert('RGBA')
            except: 
                raise UnableToDownloadImageException
            tempImg.thumbnail((32, 32), Image.LANCZOS)
            img.paste(tempImg, (coords['badge']['x']+(34*badgeNumber), coords['badge']['y']), tempImg)
            badgeNumber += 1

        # badge

        progress = (point * 100 / (level * 200))/100

        bar = self.__new_bar(1, 1, 500, 25, progress, fg=_bar_color)

        img.paste(bar, (coords['levelBar']['x'], coords['levelBar']['y']), bar)

        img.save(profil_path)

        self.__profilPath = profil_path

    def profil_path(self):
        return self.__profilPath

    # Private Methods
    def __crop_center(self, pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))

    def __crop_max_square(self, pil_img):
        return self.__crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def __mask_circle_transparent(self, pil_img, blur_radius, offset=0):
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = pil_img.copy()
        result.putalpha(mask)

        return result

    def __new_bar(self, x, y, width, height, progress, bg=(0, 0, 0, 0), fg=(173, 255, 47, 255), fg2=(15, 15, 15, 0)):
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
    # Private Methods