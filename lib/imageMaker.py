#!/usr/bin/python3
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops, ImageFilter, ImageColor
import requests
from io import BytesIO
import numpy as np
import os

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def mask_circle_transparent(pil_img, blur_radius, offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)

    return result

def new_bar(x, y, width, height, progress, bg=(0, 0, 0, 0), fg=(173,255,47,255), fg2=(15,15,15,0)):
    bar = Image.new(mode="RGBA", size=(width+(x*2)*2, height+(y*2)*2))
    draw = ImageDraw.Draw(bar)
    # Draw the background
    draw.rectangle((x+(height/2), y, x+width+(height/2), y+height), fill=fg2, width=10)
    draw.ellipse((x+width, y, x+height+width, y+height), fill=fg2)
    draw.ellipse((x, y, x+height, y+height), fill=fg2)
    width = int(width*progress)
    # Draw the part of the progress bar that is actually filled
    draw.rectangle((x+(height/2), y, x+width+(height/2), y+height), fill=fg, width=10)
    draw.ellipse((x+width, y, x+height+width, y+height), fill=fg)
    draw.ellipse((x, y, x+height, y+height), fill=fg)

    return bar

def createProfil(filePath, userName, userProfilPath, level, point, display_name, badge=[], background="default", textColor="#0000FF", barColor="#ADFF2F"):
    if not os.path.exists("img/wallpaper/"):
        os.makedirs("img/wallpaper/")
    img = Image.open('img/wallpaper/'+background).convert('RGBA').resize((500,281))

    _textColor = ImageColor.getcolor(str(textColor), "RGBA")
    _barColor = ImageColor.getcolor(str(barColor), "RGBA")

    # image
    response = requests.get(userProfilPath)
    pic = Image.open(BytesIO(response.content)).convert('RGBA').resize((128,128))

    h,w = pic.size

    pic = crop_max_square(pic).resize((w, h), Image.LANCZOS)
    pic = mask_circle_transparent(pic, 1)

    img.paste(pic, (0, 0), pic)
    # image

    # text
    d = ImageDraw.Draw(img)

    #name
    d.multiline_text((150, 20), display_name, font=ImageFont.truetype("font/ancientMedium.ttf", 45), fill=_textColor)

    d.multiline_text((150, 65), userName, font=ImageFont.truetype("font/LiberationSans-Regular.ttf", 20), fill=_textColor)

    #level
    d.multiline_text((250, 224), str(level), font=ImageFont.truetype("font/LiberationSans-Regular.ttf", 30), fill=_barColor)
    # textbarColor

    # badge

    badgeNumber = 0
    for i in badge:
        tempImg = Image.open("img/badge/"+i).convert('RGBA')
        tempImg.thumbnail((32,32), Image.ANTIALIAS)
        img.paste(tempImg, (150+(34*badgeNumber),90), tempImg)
        badgeNumber += 1

    # badge

    progress = (point * 100 / (level * 200))/100

    bar = new_bar(1, 1, 500, 25, progress, fg=_barColor)

    img.paste(bar, (0, 254), bar)

    img.save(filePath)

    return filePath

def createBar(filePath, wallpaper, coords, people):
    img = Image.open(wallpaper).convert('RGBA')

    # image
    for server in people:
        add = 0
        for member in people[server]:
            response = requests.get(member["profil"])
            pic = Image.open(BytesIO(response.content)).convert('RGBA').resize((64,64))

            h,w = pic.size

            pic = crop_max_square(pic).resize((w, h), Image.LANCZOS)
            pic = mask_circle_transparent(pic, 1)

            img.paste(pic, (coords[server]['w']+add, coords[server]['h']), pic)
            add+=int(64/(len(people[server])/3))
    # image

    img.save(filePath)
    return filePath
