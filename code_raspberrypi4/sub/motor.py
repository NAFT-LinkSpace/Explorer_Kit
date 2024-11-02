#coding: utf-8

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

from gpiozero import Motor as _Motor
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

class Motor:
    
    # 初期化
    def __init__(self):
        # DCモータのピン設定
        PIN_AIN1 = 13
        PIN_AIN2 = 19
        PIN_BIN1 = 20
        PIN_BIN2 = 21

        dcm_pins = {
            "left_forward": PIN_AIN1,
            "left_backward": PIN_AIN2,
            "right_forward": PIN_BIN1,
            "right_backward": PIN_BIN2,
        }
        
        try:
            factory = PiGPIOFactory()
            self.motor_left = _Motor( forward=dcm_pins["left_forward"],
                                backward=dcm_pins["left_backward"],
                                pin_factory=factory)
            self.motor_right = _Motor( forward=dcm_pins["right_forward"],
                                backward=dcm_pins["right_backward"],
                                pin_factory=factory)
            self.isAvailable = True
        except Exception as e:
            logger.error("TCE: Motor Init Error ->" + str(e))
            self.isAvailable = False
    
    # 左のモータを指定された出力で回転させる
    def left(self, power):
        if self.isAvailable:
            self.motor_left.value = power # power: 0.0 ~ 1.0
        
    # 右のモータを指定された出力で回転させる
    def right(self, power):
        if self.isAvailable:
            self.motor_right.value = power # power: 0.0 ~ 1.0
        
    # 両方のモータを停止させる
    def stop(self):
        self.left(0.0)
        self.right(0.0)

# このファイルが実行されたときの処理
if __name__ == "__main__":
    motor = Motor()
    motor.left(1.0)
    motor.right(1.0)
    sleep(3)
    motor.stop()
    sleep(1)
    motor.left(-0.5)
    motor.right(-0.5)
    sleep(3)
    motor.stop()
