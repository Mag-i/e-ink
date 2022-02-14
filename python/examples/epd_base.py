#!/usr/bin/python
# -*- coding:utf-8 -*-
from doctest import master
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from lib.rpi_epd2in7_master.epd import EPD
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    epd = EPD()
    epd.init()
    epd.Clear(0xFF)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    pic = Image.new('1', (epd.height, epd.width), 255)
    bmp = Image.open(os.path.join(picdir, 'base.bmp'))
    pic.paste(bmp, (0, 0))
    epd.display_frame(epd._get_frame_buffer(pic))
    time.sleep(2)
    draw = ImageDraw.Draw(pic)
    full_update = False
    while True:
        for i in range(0, 200000):
            value = i
            draw.text((5, 5), value, font=font35, fill=0)
            epd.display_partial_frame(pic, 0, 25, 20, epd.width, fast=True)
            
except KeyboardInterrupt:
        epd.sleep()
        print("Bye!")
        raise