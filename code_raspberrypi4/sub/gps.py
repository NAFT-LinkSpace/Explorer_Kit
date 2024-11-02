#coding: utf-8

# 参考文献
# Ambient: Raspberry Pi3のPythonでGPSを扱う
# https://ambidata.io/blog/2017/08/02/gps/

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import serial
import micropyGPS
import threading
import time

class GPS:
    
    # 初期化
    def __init__(self, _main):
        self.gps = micropyGPS.MicropyGPS(9, 'dd') # MicroGPSオブジェクトを生成する。
        # 引数はタイムゾーンの時差と出力フォーマット
        
        self.uart = serial.Serial('/dev/serial0', 9600, timeout=10)
        
        self.main = _main
        
        self.isGPSReadMode = False # GPSを定期的に読み取るモード
        self.isGPSConvertMode = False # GPSのデータを変換するモード
        
        self.isSendSentenceMode = False # GPSからの生データをSkyWayに送信するモード
        self.isSendConvertedDataMode = False # GPSの変換されたデータをSkyWayに送信するモード

        self.isRandomMode = False # ランダムな座標をSkyWayに送信するモード
        
        self.totalSentence = ""
        self.sentenceLogInterval = 5 # GPSのデータを送信する頻度[s]
    
    # GPSモジュールからのデータ受信を開始する関数
    def startReceive(self):
        self.isGPSReadMode = True
        gpsthread = threading.Thread(target=self.run, args=())
        gpsthread.daemon = True
        gpsthread.start()
    
    # GPSモジュールからデータを定期的に読み取る関数
    def run(self):
        sentenceLogCount = 0
        self.totalSentence = ""
        self.uart.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる
        while self.isGPSReadMode:
            sentence = self.uart.readline().decode('utf-8') # GPSデーターを読み、文字列に変換する
            if sentence[0] != '$': # 先頭が'$'でなければ捨てる
                continue
            
            if self.isSendSentenceMode:
                if ("GPGGA" in sentence):
                    if sentenceLogCount % self.sentenceLogInterval == 0 and self.main != None:
                        self.main.send_prompt_data("GPS Raw Data", self.totalSentence)
                    sentenceLogCount = sentenceLogCount + 1
                    self.totalSentence = sentence
                else:
                    self.totalSentence = self.totalSentence + sentence
            
            for x in sentence: # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
                self.gps.update(x)
                
    # GPSモジュールから得られた生データの変換を開始する関数
    def startConvert(self):
        self.isGPSConvertMode = True
        convertthread = threading.Thread(target=self.convert, args=()) # 上の関数を実行するスレッドを生成
        convertthread.daemon = True
        convertthread.start() # スレッドを起動
    
    # GPSモジュールから得られた生データの変換をする関数
    def convert(self):
        while self.isGPSConvertMode:
            if self.gps.clean_sentences > 20: # ちゃんとしたデーターがある程度たまったら出力する
                h = self.gps.timestamp[0] if self.gps.timestamp[0] < 24 else self.gps.timestamp[0] - 24
                gpsStr = str('%2d:%02d:%04.1f' % (h, self.gps.timestamp[1], self.gps.timestamp[2]))
                gpsStr = gpsStr + str('\n緯度経度: %2.8f, %2.8f' % (self.gps.latitude[0], self.gps.longitude[0]))
                gpsStr = gpsStr + str('\n海抜: %f' % self.gps.altitude)
                gpsStr = gpsStr + str('\n測位利用衛星: ' + str(self.gps.satellites_used))
                gpsStr = gpsStr + str('\n衛星番号: (仰角, 方位角, SN比)')
                try:
                    for k, v in self.gps.satellite_data.items():
                        gpsStr = gpsStr + str('\n%d: %s' % (k, v))
                except Exception as e:
                    logger.error("TCE: GPS Convert Error ->" + str(e))
                    gpsStr = gpsStr + "Error while getting satellite data"
                if self.isSendConvertedDataMode and self.main != None:
                    self.main.send_prompt_data("GPS Converted Data", gpsStr)
                logger.info("Converted GPS Data: " + gpsStr)
            time.sleep(5.0)
    
    # GPSからのデータを取得する関数
    def getData(self):
        
        # main.pyで使用するデータに変換
        data = {}
        
        logger.debug("Start Getting GPS Data")
        data["status"] = True
        data["latitude"] = self.gps.latitude[0]
        data["longitude"] = self.gps.longitude[0]
        
        # 緯度経度の情報が無かったら破棄する
        if (data["latitude"] == 0 and data["longitude"] == 0):
            data["status"] = False
            try:
                data.pop("latitude")
                data.pop("longitude")
            except Exception as e:
                logger.error("TCE: Error on GPS pop ->" + str(e))
                
        # 緯度経度の情報をランダムに設定する
        if self.isRandomMode == True:
            import random
            data["status"] = True
            data["latitude"] = random.random() * 0.001 + 35.1855875
            data["longitude"] = random.random() * 0.001 + 136.8990919
        
        logger.debug("Finish Getting GPS Data")
        
        return data
        
# このファイルが実行されたときの処理
if __name__ == "__main__":
    gps = GPS(None)
    gps.startReceive()
    gps.startConvert()
    x = 0
    while True:
        x = x + 1
    