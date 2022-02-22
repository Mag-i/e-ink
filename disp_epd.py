from __future__ import print_function
from lib.epd import EPD
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
if sys.version_info.major < 3:
    input = raw_input

# This demo shows usage of both display_frame and display_partial_frame


def main():
    print("initializing...")
    epd = EPD()
    epd.init()

    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    bmp = Image.open('base.bmp')
    image.paste(bmp, (50, 10))
    epd.display_frame(image)
    time.sleep(2)

    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    epd.display_frame(image)
    loc = 25
    full_update = False
    print("Ready.")
    try:
        while True:
            text = input("> ")
            if loc > epd.height - 10:
                loc = 0
                image = Image.new('1', (epd.width, epd.height), 255)
                draw = ImageDraw.Draw(image)
                full_update = True

            draw.text((5, loc), text, font=font, fill=0)
            if full_update:
                print("Doing a full update...")
                epd.display_frame(image)
                full_update = False
            else:
                print("...")
                epd.display_partial_frame(image, 0, loc, 20, epd.width, fast=True)

            loc += 20
    except KeyboardInterrupt:
        epd.sleep()
        print("Bye!")
        raise


if __name__ == '__main__':
    main()