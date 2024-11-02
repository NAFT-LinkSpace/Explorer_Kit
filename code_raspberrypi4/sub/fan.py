#coding: utf-8

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import RPi.GPIO as GPIO
from time import sleep

class Fan:
    def __init__(self):
        self.FAN_PIN = 0 # ファンのGPIO
        self.isForce = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.FAN_PIN, GPIO.OUT)
    
    # ファンをONにする関数
    def on(self):
        try:
            GPIO.output(self.FAN_PIN, GPIO.HIGH)
        except Exception as e:
            logger.error("TCE: Fan Error ->" + str(e))
    
    # ファンをOFFにする関数
    def off(self):
        try:
            GPIO.output(self.FAN_PIN, GPIO.LOW)
        except Exception as e:
            logger.error("TCE: Fan Error ->" + str(e))
            
    # ファンのAUTOモードをONにする関数
    def on_auto(self):
        if self.isForce == False:
            self.on()
    
    # ファンのAUTOモードをOFFにする関数
    def off_auto(self):
        if self.isForce == False:
            self.off()
        

# このファイルが実行されたときの処理
if __name__ == "__main__":
    print("START")
    fan = Fan()
    fan.off()
    sleep(5.0)
    fan.on()