# *****************************************************************************
# * | File        :	  epd2in7.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from __future__ import unicode_literals, division, absolute_import

import time
import spidev
from .lut import LUT, QuickLUT
import RPi.GPIO as GPIO
from PIL import ImageChops
import logging
from . import epdconfig

# Display resolution
EPD_WIDTH       = 176
EPD_HEIGHT      = 264

# Pin definition
RST_PIN         = 17
DC_PIN          = 25
CS_PIN          = 8
BUSY_PIN        = 24

GRAY1  = 0xff #white
GRAY2  = 0xC0
GRAY3  = 0x80 #gray
GRAY4  = 0x00 #Blackest

logger = logging.getLogger(__name__)

class EPD:
    def __init__(self, partial_refresh_limit=32, fast_refresh=True):
        self.fast_refresh = fast_refresh
        """ enable or disable the fast refresh mode """
        self.partial_refresh_limit = partial_refresh_limit
        """ number of partial refreshes before a full refrersh is forced """
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.GRAY1  = GRAY1 #white
        self.GRAY2  = GRAY2
        self.GRAY3  = GRAY3 #gray
        self.GRAY4  = GRAY4 #Blackest
        self._last_frame = None
        self._partial_refresh_count = 0
        self._init_performed = False
        self.spi = spidev.SpiDev(0, 0)
 
    def digital_write(self, pin, value):
        return GPIO.output(pin, value) 
       
    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)
    
    # Hardware reset
    def reset(self):
        self.digital_write(RST_PIN, GPIO.LOW)
        self.delay_ms(200)
        self.digital_write(RST_PIN, GPIO.HIGH)
        self.delay_ms(200)  

    def send_command(self, command):
        self.digital_write(DC_PIN, GPIO.LOW)
        self.spi.writebytes([command])

    def send_data(self, data):
        self.digital_write(DC_PIN, GPIO.HIGH)
        self.spi.writebytes([data])
        
    def wait_until_idle(self):
        """ Wait until screen is idle by polling the busy pin """
        # HACK: fix e-Paper not picking up ready signal and getting stuck in busy state
        # https://github.com/waveshare/e-Paper/issues/30#issuecomment-640254220
        self.send_command(0x71)
        while(self.digital_read(BUSY_PIN) == 0):      # 0: busy, 1: idle
            self.send_command(0x71)
            self.delay_ms(50)
        

    def set_lut(self):
        """ Set LUT for the controller.
        If `fast` is srt to True, quick update LUTs from Ben Krasnow will be used"""
        lut_to_use = LUT if not fast else QuickLUT

        # Quick LUTs courtsey of Ben Krasnow:
        # http://benkrasnow.blogspot.co.il/2017/10/fast-partial-refresh-on-42-e-paper.html
        # https://www.youtube.com/watch?v=MsbiO8EAsGw

        self.send_command(LUT_FOR_VCOM)               # vcom
        for byte in lut_to_use.lut_vcom_dc:
            self.send_data(byte)

        self.send_command(LUT_WHITE_TO_WHITE)         # ww --
        for byte in lut_to_use.lut_ww:
            self.send_data(byte)

        self.send_command(LUT_BLACK_TO_WHITE)         # bw r
        for byte in lut_to_use.lut_bw:
            self.send_data(byte)

        self.send_command(LUT_WHITE_TO_BLACK)         # wb w
        for byte in lut_to_use.lut_wb:
            self.send_data(byte)

        self.send_command(LUT_BLACK_TO_BLACK)         # bb b
        for byte in lut_to_use.lut_bb:
            self.send_data(byte)
            
    
    def init(self):
        """ Preform the hardware initialization sequence """
        # Interface initialization:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0b00
        # EPD hardware init
        # The specifics of how this works or what "power optimization" actually means
        # are unclear to me, so I'm leaving it as-is.
        self.reset()
        self.send_command(POWER_SETTING)
        self.send_data(0x03)                  # VDS_EN, VDG_EN
        self.send_data(0x00)                  # VCOM_HV, VGHL_LV[1], VGHL_LV[0]
        self.send_data(0x2b)                  # VDH
        self.send_data(0x2b)                  # VDL
        self.send_data(0x09)                  # VDHR
        self.send_command(BOOSTER_SOFT_START)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x17)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x60)
        self.send_data(0xA5)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x89)
        self.send_data(0xA5)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x90)
        self.send_data(0x00)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x93)
        self.send_data(0x2A)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0xA0)
        self.send_data(0xA5)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0xA1)
        self.send_data(0x00)
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x73)
        self.send_data(0x41)
        self.send_command(PARTIAL_DISPLAY_REFRESH)
        self.send_data(0x00)
        self.send_command(POWER_ON)
        self.wait_until_idle()

        self.send_command(PANEL_SETTING)
        self.send_data(0xAF)        # KW-BF   KWR-AF    BWROTP 0f
        self.send_command(PLL_CONTROL)
        self.send_data(0x3A)        # 3A 100HZ   29 150Hz 39 200HZ    31 171HZ
        self.send_command(VCM_DC_SETTING_REGISTER)
        self.send_data(0x12)
        self.delay_ms(2)
        self.set_lut()
        # EPD hardware init end
        self._init_performed = True

    def getbuffer(self, image):
        # logger.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # logger.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if(imwidth == self.width and imheight == self.height):
            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logger.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf
    
                        
        elif(imwidth == self.height and imheight == self.width):
            logger.debug("Horizontal")
            for x in range(imwidth):
                for y in range(imheight):
                    newx = y
                    newy = self.height - x - 1
                    if(pixels[x, y] == 0xC0):
                        pixels[x, y] = 0x80
                    elif (pixels[x, y] == 0x80):
                        pixels[x, y] = 0x40
                    i= i+1
                    if(i%4 == 0):
                        buf[int((newx + (newy * self.width))/4)] = ((pixels[x, y-3]&0xc0) | (pixels[x, y-2]&0xc0)>>2 | (pixels[x, y-1]&0xc0)>>4 | (pixels[x, y]&0xc0)>>6) 
        return buf
    
    def display(self, image):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(image[i])
        self.send_command(0x12) 
        self.ReadBusy()

        
    def Clear(self, color=0xFF):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(color)
        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(color)
        self.send_command(0x12) 
        self.ReadBusy()

    def sleep(self):
        self.send_command(0X50)
        self.send_data(0xf7)
        self.send_command(0X02)
        self.send_command(0X07)
        self.send_data(0xA5)
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
### END OF FILE ###
