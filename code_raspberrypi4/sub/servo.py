#coding: utf-8

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

class Servo:
    
    # 初期化
    def __init__(self):
        # SG90のピン設定
        SERVO_PIN = 12

        MIN_DEGREE = -90       # 000 : -90degree
        MAX_DEGREE = 90       # 180 : +90degree

        try:
            factory = PiGPIOFactory()
            # min_pulse_width, max_pulse_width, frame_width =>SG90仕様
            self.servo = AngularServo(SERVO_PIN, initial_angle=-60, min_angle=MIN_DEGREE, max_angle=MAX_DEGREE, 
                                min_pulse_width=0.5/1000, max_pulse_width=2.4/1000, frame_width=1/50,
                                pin_factory=factory)
            self.isAvailable = True
        except Exception as e:
            logger.error("TCE: Servo Init Error ->" + str(e))
            self.isAvailable = False
    
    # サーボを指定された角度に動かす
    def angle(self, angle):
        if self.isAvailable :
            self.servo.angle = angle

# このファイルが実行されたときの処理
if __name__ == "__main__":
    servo = Servo()
    try:
        for _ in range(5):
            servo.angle = 60
            sleep(1.0)
            servo.angle = -60
            sleep(1.0)
    except KeyboardInterrupt:
        print("stop")
