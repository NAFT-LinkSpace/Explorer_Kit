#coding: utf-8

# 参考文献
# PyPI: adafruit-circuitpython-ssd1331 1.4.1
# https://pypi.org/project/adafruit-circuitpython-ssd1331/

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import board
import displayio
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
import terminalio
from adafruit_display_text import label
from adafruit_ssd1331 import SSD1331

class Display:
    
    # 初期化
    def __init__(self):
        spi = board.SPI()
        tft_cs = board.D7
        tft_dc = board.D26

        displayio.release_displays()
        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.D4)

        display = SSD1331(display_bus, rotation=180, width=96, height=64)

        # Make the display context
        self.splash = displayio.Group()
        display.root_group = self.splash

        color_bitmap = displayio.Bitmap(96, 64, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0x00FF00 # Bright Green

        bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
        self.splash.append(bg_sprite)
    
    # 四角形を描き出す関数
    def draw_rectangle(self):
        # Draw a smaller inner rectangle
        inner_bitmap = displayio.Bitmap(86, 54, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0xAA0088 # Purple
        inner_sprite = displayio.TileGrid(inner_bitmap,
                                  pixel_shader=inner_palette,
                                  x=5, y=5)
        self.splash.append(inner_sprite)
    
    # 引数textを表示する関数
    def draw_label(self, text):
        # Draw a label
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=12, y=32)
        self.splash.append(text_area)
        
# このファイルが実行されたときの処理
if __name__ == "__main__":
    display = Display()
    display.draw_rectangle()
    display.draw_label("Hello World!")


