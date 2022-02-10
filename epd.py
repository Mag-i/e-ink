#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from gpiozero import Button

btn1 = Button(5) # Assign btn to the button on the HAT at pin 5
btn2 = Button(6) # Assign btn to the button on the HAT at pin 6
btn3 = Button(13) # Assign btn to the button on the HAT at pin 13
btn4 = Button(19) # Assign btn to the button on the HAT at pin 19

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in7 Demo")   
    epd = epd2in7.EPD()
    
    logging.info("init and Clear")
    epd.init()                                                                  # initialize unit
    epd.Clear(0xFF)                                                             # clearing screen
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    
    logging.info("Drawing borders")
    pic = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    bmp = Image.open(os.path.join(picdir, '2in7.bmp'))  # Load 'template'
    pic.paste(bmp, (50,10))                             # Paste pic on frame
    epd.display(epd.getbuffer(pic))                     # Update display
    time.sleep(2)
    
    
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()