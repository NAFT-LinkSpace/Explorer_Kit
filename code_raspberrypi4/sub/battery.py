#coding: utf-8

# 参考文献
# JOSEPHHALFMOON：部品屋根性(74) MCP3421、18bit ΔΣADCをRaspberry Piに接続
# https://jhalfmoon.com/dbc/2022/07/21/部品屋根性74-mcp3421、18bit-δσadcをraspberry-piに接続

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import pigpio
import time

class Battery:
    
    # 初期化
    def __init__(self):
        try:
            device = 0x68 #MCP3421のアドレス(I2C)
            self.pi = pigpio.pi()
            self.handle = self.pi.i2c_open(1, device) # I2C通信開始
            self.pi.i2c_write_byte(self.handle, 0x18) # I2C初期化データ送信
            self.isAvailable = True
        except Exception as e:
            logger.error("TCE: Battery Init Error ->" + str(e))
            self.isAvailable = False
            
    # MCP3421からバッテリー電圧を取得する関数
    def getData(self):
        (count, data) = self.pi.i2c_read_device(self.handle, 3) # I2C受信
        
        voltage = 0
        
        # 受信したデータを電圧に変換する
        if len(data) == 3:
            data_num = data[0] * 256 + data[1]
            voltage_raw = data_num / 32767 * 2.048
            voltage = voltage_raw / 11
            
        # main.pyで使用するデータに変換
        main_data = {}
        if self.isAvailable:
            main_data["status"] = True
            main_data["voltage"] = voltage
        else: 
            main_data["status"] = False
        
        return main_data
    
    # MCP3421からバッテリー電圧を取得する関数(デバッグ用)
    def getDataDebug(self):
        (count, data) = self.pi.i2c_read_device(self.handle, 3)
        print("count: {0} len: {1}".format(count, len(data)))
        if len(data) == 3:
            data_num = data[0] * 256 + data[1]
            voltage_raw = data_num / 32767 * 2.048
            voltage = voltage_raw / 2 * 33
            print("Data: {0} ".format(data_num))
            print("2進数:" + str(bin(data_num)))
            print("電圧: " + str(voltage_raw) + " V")
            print("正しい電圧: " + str(voltage) + " V")
            print("CONTROL: {0:02x}".format(data[2]))
            
    # MCP3421とのI2C通信を終了する関数
    def closeI2C(self):
        self.pi.i2c_close(self.handle)


# このファイルが実行されたときの処理
if __name__ == "__main__":
    battery = Battery()
    battery.getData() # 最初のデータは捨てる
    time.sleep(1)
    x = battery.getData()
    if x["status"] == True:
        print("voltage :",x["voltage"],"V")
    else:
        print("Battery No Data")