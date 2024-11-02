#coding: utf-8

# 参考文献
# adafruit: Adafruit BNO055 Absolute Orientation Sensor > Python & CircuitPython
# https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/python-circuitpython

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import board
import adafruit_bno055

class BNO055:
    
    # 初期化
    def __init__(self):
        try:
            self.i2c = board.I2C()
            self.sensor = adafruit_bno055.BNO055_I2C(self.i2c)
            self.isAvailable = True
        except Exception as e:
            logger.error("TCE: BNO055 Init Error ->" + str(e))
            self.isAvailable = False
            
        # 記録するデータの種類 True:記録, False:記録しない
        self.log_bno_data = [
            False, # Temperature(温度) [degrees C]
            True, # Accelerometer(加速度) [m/s^2]
            True, # Magnetometer(磁力) [microteslas]
            True, # Gyroscope(角速度) [rad/sec]
            True, # Euler angle(オイラー角) []
            True, # Quaternion(四元数) []
            True, # Linear acceleration(直線加速度) [m/s^2]
            True  # Gravity(重力) [m/s^2]
            ]
        
    # BNO055からデータを取得する関数
    def getData(self):
        
        # main.pyで使用するデータに変換
        data = {}
    
        if self.isAvailable:
            try:
                if self.log_bno_data[0] and self.sensor.temperature != None: data["temeprature"] = self.sensor.temperature
                if self.log_bno_data[1] and self.sensor.acceleration != None: data["accelerometer"] = self.sensor.acceleration 
                if self.log_bno_data[2] and self.sensor.magnetic != None: data["magnetometer"] = self.sensor.magnetic 
                if self.log_bno_data[3] and self.sensor.gyro != None: data["gyroscope"] = self.sensor.gyro 
                if self.log_bno_data[4] and self.sensor.euler != None: data["euler_angle"] = self.sensor.euler 
                if self.log_bno_data[5] and self.sensor.quaternion != None: data["quaternion"] = self.sensor.quaternion 
                if self.log_bno_data[6] and self.sensor.linear_acceleration != None: data["linear_acceleration"] = self.sensor.linear_acceleration 
                if self.log_bno_data[7] and self.sensor.gravity != None: data["gravity"] = self.sensor.gravity 
            except Exception as e:
                logger.info(e)
                data = {}
        
        data["status"] = False if data == {} else True
        
        return data

# このファイルが実行されたときの処理
if __name__ == "__main__":
    bno055 = BNO055()
    print(bno055.getData())
