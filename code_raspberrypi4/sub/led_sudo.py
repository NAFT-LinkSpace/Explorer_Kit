#coding: utf-8

# 参考文献
# adafruit: NeoPixel LEDs
# https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/neopixel-leds

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import sys
import board
import neopixel
import rainbowio

args = sys.argv

num_leds = 6 # LEDの個数
leds = neopixel.NeoPixel(board.D18, num_leds, brightness=0.1, auto_write=False, pixel_order=neopixel.RGB)


if len(args) >= 5:
    # 引数が5個以上ある場合、引数を読み取る
    n = int(args[1])
    r = int(args[2])
    g = int(args[3])
    b = int(args[4])
    
    # LEDの色を決める
    for l in range(len(leds)):
       leds[l] = (r, g, b)
    
    # LEDを光らせる
    leds.show()
else:
    # 引数が無い場合は虹色に光らせる
    delta_hue = 256//num_leds
    speed = 2  # higher numbers = faster rainbow spinning
    i = 0
    while i < 1000:
       i = i + 1
       for l in range(len(leds)):
        leds[l] = rainbowio.colorwheel( int(i*speed + l * delta_hue) % 255  )
        leds.show()  # only write to LEDs after updating them all
        i = (i+1) % 255

