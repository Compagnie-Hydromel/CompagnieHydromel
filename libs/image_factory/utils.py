from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
import os
class Utils():

    @staticmethod
    def pillow_crop_max_square(pil_img: Image) -> Image:
        """This method is designed to crop a pillow image to a max square.

        Args:
            pil_img (Image): The pillow image.

        Returns:
            Image: The pillow image cropped.
        """
        return Utils.pillow_crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    @staticmethod
    def pillow_mask_circle_transparent(pil_img: Image, blur_radius: float, offset: int = 0) -> Image:
        """This method is designed to mask a pillow image to a circle.

        Args:
            pil_img (Image): The pillow image.
            blur_radius (float): The blur radius.
            offset (int, optional): The offset. Defaults to 0.

        Returns:
            Image: The pillow image masked.
        """
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = pil_img.copy()
        result.putalpha(mask)

        return result

    @staticmethod
    def pillow_new_bar(x: int, y: int, width: int, height: int, progress: int, fg=(173, 255, 47, 255), bg=(0, 0, 0, 0)) -> Image:
        """This method is designed to create a new bar in an image.

        Args:
            x (int): The x postition of the new bar.
            y (int): The y postition of the new bar.
            width (int): the width of the new bar. 
            height (int): the height of the new bar.
            progress (int): The level of progress of the new bar in percentage.
            fg (tuple, optional): The forground color. Defaults to (173, 255, 47, 255).
            bg (tuple, optional): The background color. Defaults to (0, 0, 0, 0).

        Returns:
            Image: The image with the new bar.
        """
        bar = Image.new(mode="RGBA", size=(width+(x*2)*2, height+(y*2)*2))
        draw = ImageDraw.Draw(bar)

        # Draw the background
        draw.rectangle((x+(height/2), y, x+width+(height/2),
                       y+height), fill=bg, width=10)
        draw.ellipse((x+width, y, x+height+width, y+height), fill=bg)
        draw.ellipse((x, y, x+height, y+height), fill=bg)
        width = int(width*progress)

        # Draw the part of the progress bar that is actually filled
        draw.rectangle((x+(height/2), y, x+width+(height/2),
                       y+height), fill=fg, width=10)
        draw.ellipse((x+width, y, x+height+width, y+height), fill=fg)
        draw.ellipse((x, y, x+height, y+height), fill=fg)

        return bar
    
    @staticmethod
    def pillow_crop_center(pil_img: Image, crop_width: int, crop_height: int) -> Image:
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))

    @staticmethod
    def analyseImage(image: BytesIO):
        '''
        Pre-process pass over the image to determine the mode (full or additive).
        Necessary as assessing single frames isn't reliable. Need to know the mode 
        before processing all frames.
        '''
        im = Image.open(image)
        results = {
            'size': im.size,
            'mode': 'full',
        }
        try:
            while True:
                if im.tile:
                    tile = im.tile[0]
                    update_region = tile[1]
                    update_region_dimensions = update_region[2:]
                    if update_region_dimensions != im.size:
                        results['mode'] = 'partial'
                        break
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        return results

    @staticmethod
    def gif_to_image_list(image: BytesIO):
        mode = Utils.analyseImage(image)['mode']
        
        frames: list[Image.Image] = []
        
        im = Image.open(image)

        i = 0
        last_frame = im.convert('RGBA')
        
        try:
            while True:
                new_frame = Image.new('RGBA', im.size)

                if mode == 'partial':
                    new_frame.paste(last_frame)
                
                new_frame.paste(im, (0,0), im.convert('RGBA'))
                frames.append(new_frame)

                i += 1
                last_frame = new_frame
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        
        return frames
