#!/usr/bin/env python3

import logging
import datetime

# -----logファイル設定 ここから-----
# DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL

# main.pyの絶対アドレス＆ディレクトリ取得
main_path = globals()['__file__'] # str       
main_dir = main_path[:-7]

# loggerの定義＆設定
logger = logging.getLogger("メインログ")
logger.setLevel(logging.DEBUG)

# ログの書式の設定
format = "%(levelname)-9s  %(asctime)s [%(filename)s:%(lineno)d] %(message)s"

# コンソールに送るログの設定
st_handler = logging.StreamHandler()
st_handler.setLevel(logging.DEBUG)
st_handler.setFormatter(logging.Formatter(format))

# logフォルダに追加するファイル名の設定
dt_now = datetime.datetime.now()
log_filename = main_dir + "/log/" + dt_now.strftime('%Y-%m-%d_%H-%M-%S') + ".log"

# logフォルダに送るログの設定
fl_handler = logging.FileHandler(filename=log_filename, encoding="utf-8")
fl_handler.setLevel(logging.DEBUG)
fl_handler.setFormatter(logging.Formatter(format))

# ハンドラ設定
logger.addHandler(st_handler)
logger.addHandler(fl_handler)

# loggerのexample
# logger.info("I am info log.")
# logger.warning("I am warning log.")

# -----ここまで-----

# subファイル内のpyファイルのインポート
from sub import _flask
from sub import battery
from sub import bno055
from sub import bme280
from sub import browser
from sub import buzzer
from sub import cpu
from sub import fan
from sub import gps
from sub import led
from sub import motor
from sub import servo

# 通常インポート
import threading
import time
import os
import subprocess
from urllib import request

class Main:

    # 初期化
    def __init__(self):
        logger.debug("Initing Main")
        
        # パス（文字列）をクラス内で再定義
        self.main_path = main_path
        self.main_dir = main_dir
        logger.info("Got main path: " + self.main_path)
        logger.info("Got main dir: " + self.main_dir)

        # データを記録する間隔[sec]を設定
        self.log_interval = 2.0

        # 通信関係
        self.send_data_list = [] # 送るデータはリストとしてここに追加される
        _flask.main = self # _flask.pyからmainにアクセスできるように
        
        # 各クラス初期化
        self.battery = battery.Battery()
        self.bme280 = bme280.BME280()
        self.bno055 = bno055.BNO055()
        self.browser = browser.Browser()
        self.buzzer = buzzer.Buzzer()
        self.cpu = cpu.CPU()
        self.fan = fan.Fan()
        self.gps = gps.GPS(self)
        self.led = led.LED()
        self.motor = motor.Motor()
        self.servo = servo.Servo()
        
        # カメラから送られてくる映像をchromeで使えるように
        subprocess.Popen( ["lxterminal", "-e", "gst-launch-1.0 libcamerasrc ! \"video/x-raw,width=1280,height=1080,format=YUY2\",interlace-mode=progressive ! videoconvert ! v4l2sink device=/dev/video8" ])
        
        # 画像認識を使う際のコード
        # subprocess.Popen( ["lxterminal", "-e", "python " + main_dir + "sub/camera.py"])

        # Flask開始
        flaskThread = threading.Thread(target=_flask.app.run, args=[])
        flaskThread.start()

        # ブラウザを一番前に表示する
        self.browser.switch_window()

        # ネット環境確認【フェーズ移行】
        self.check_internet()

    # ネット環境確認
    def check_internet(self):
        logger.info("Checking Internet Connection")

        try:
            # googleにアクセスできるか試みる(3s)
            request.urlopen('https://google.com', timeout=3)

            # 接続できた（エラーが発生しなかった）
            logger.info("Internet Connection Success")
            # ブラウザ起動
            browserThread = threading.Thread(target=self.browser.open_browser, args=[])
            browserThread.start()

            # 定期通信確認開始
            self.skyway_connection_checker_start()
            
            # 定期的なログの出力開始
            t1 = threading.Thread(target=self.send_interval_data, args=[])
            t1.start()

        except request.URLError as err:
            # 接続できず（エラーが発生した）
            logger.info("TCE: Internet Connection Failed")
            time.sleep(3)
            self.check_internet()

    # 定期的にデータをSkyWayに送信する関数
    def send_interval_data(self):
        
        # GPSの定期データ処理
        if self.gps.isGPSReadMode == False:
            self.gps.startReceive()
        if self.gps.isGPSConvertMode == False:
            self.gps.startConvert()
        
        data = {}
        last_run_time = time.time()
        while True:
            # データを記録する間隔だけ時間を空けたか確認
            if time.time() - last_run_time >= self.log_interval :
                logger.debug("Start getting interval log data")
                last_run_time = time.time()

                data["data_type"] = "interval"

                # 各センサ等からデータを取得
                battery_data = self.battery.getData()
                data["battery"] = battery_data
                bno_data = self.bno055.getData()
                data["bno055"] = bno_data
                bme_data = self.bme280.getData()
                data["bme280"] = bme_data
                gps_data = self.gps.getData()
                data["gps"] = gps_data
                cpu_data = self.cpu.getData()
                data["cpu"] = cpu_data

                # CPU温度が60℃以上だった場合ファンを回す
                if type(cpu_data["temp"]) is float:
                    if cpu_data["temp"] >= 60:
                        self.fan.on_auto()
                    else:
                        self.fan.off_auto()
                
                # 出来たデータを記録
                logger.debug("Interval Log Data: " + str(data))

                self.send_data_list.append(data) # データ送信リストに追加

                logger.debug("Finish getting interval log data")
    
    # 即座にデータをSkyWayに送信する関数
    def send_prompt_data(self, title, detail):
        log_data = {}
        log_data["title"] = title
        log_data["detail"] = detail
        data = {}
        data["data_type"] = "prompt"
        data["log"] = log_data

        self.send_data_list.append(data) # データ送信リストに追加

    # 即座にデータをSkyWayに送信する関数(RETURN)
    def send_return_data(self, title, detail):
        log_data = {}
        log_data["title"] = title
        log_data["detail"] = detail
        data = {}
        data["data_type"] = "return"
        data["log"] = log_data

        self.send_data_list.append(data) # データ送信リストに追加
        
    # 即座にデータをSkyWayに送信する関数(ConnectionCheck)
    def send_connection_check_pong(self):
        data = {}
        data["data_type"] = "ConnectionCheckPong"

        self.send_data_list.append(data) # データ送信リストに追加

    # data_received関数を別スレッドで実行する関数
    def data_received_async(self, received_data):
        dataReceivedThread = threading.Thread(target=self.data_received, args=(received_data, ))
        dataReceivedThread.start()

    # SkyWayからデータを受信したときに実行される関数
    def data_received(self, received_data):
        # JavaScriptのプログラムからデータが送られてきていた場合
        if "SkyWayProgressId" in str(received_data):
            logger.info("Got Data from JavaScript (SkyWay Progress): " + received_data)
            id = -1
            try:
                id = float(str(received_data).replace("SkyWayProgressId", ""))
            except Exception as e:
                logger.error("TCE: SkyWay Progress Id Convert Error ->" + str(e))
            if id == 0 :
                self.skyway_restarted()
        elif received_data != "": # SkyWayからデータが送られてきていた場合
            logger.info("Got Data from SkyWay: " + received_data)
            
            if ("ConnectionCheckPing" in str(received_data)) == False:
                # 送られてきたコードをそのまま返す
                self.send_return_data("Return Log", str(received_data))
            
            if "ConnectionCheckPing" in str(received_data):
                # 定期確認
                logger.info("App: Connection check ping received")
                self.skyWayConnectionCheck = True
                self.send_connection_check_pong()

            elif "restart" in str(received_data):
                # プログラムだけ再起動
                logger.info("App: Restart")
                self.browser.close_browser()
                subprocess.run("sudo systemctl restart test.service", shell=True)

            elif "reboot" in str(received_data):
                # ラズパイ再起動
                logger.info("App: Reboot")
                os.system('sudo reboot')

            elif "getGPScon" in str(received_data):
                # GPSデータ送信
                logger.info("App: Prepare send GPS data")
                if self.gps.isGPSReadMode == False:
                    self.gps.startReceive()
                if self.gps.isGPSConvertMode == False:
                    self.gps.startConvert()
                self.gps.isSendConvertedDataMode = True

            elif "getGPSraw" in str(received_data):
                # GPSの生データ送信
                logger.info("App: Prepare send raw GPS data")
                if self.gps.isGPSReadMode == False:
                    self.gps.startReceive()
                self.gps.isSendSentenceMode = True

            elif "onGPSran" in str(received_data):
                # GPSの生データ送信
                logger.info("App: GPS random mode ON")
                self.gps.isRandomMode = True

            elif "offGPSran" in str(received_data):
                # GPSの生データ送信終了
                logger.info("App: GPS random mode OFF")
                self.gps.isRandomMode = False

            elif "stopGPS" in str(received_data):
                # GPSデータ終了
                logger.info("App: End GPS data")
                self.gps.isGPSReadMode = False
                self.gps.isGPSConvertMode = False
                self.gps.isSendSentenceMode = False
                self.gps.isSendConvertedDataMode = False

            elif "ping" in str(received_data):
                # pingpong
                logger.info("App: PingPong")
                self.send_prompt_data("PP Log", "pong")

            elif "leftMotor" in str(received_data):
                # 左モータ
                power = 0.0
                try:
                    power = float(str(received_data).replace("leftMotor", ""))
                except Exception as e:
                    logger.error("TCE: App: Left Motor Error ->" + str(e))
                logger.info("App: LeftMotor:" + str(power))
                self.motor.left(power)

            elif "rightMotor" in str(received_data):
                # 右モータ
                power = 0.0
                try:
                    power = float(str(received_data).replace("rightMotor", ""))
                except Exception as e:
                    logger.error("TCE: App: Right Motor Error ->" + str(e))
                logger.info("App: RightMotor:" + str(power))
                self.motor.right(power)

            elif "bothMotor" in str(received_data):
                # モータ両方
                left_power = 0.0
                right_power = 0.0
                try:
                    both_data = str(received_data).replace("bothMotor", "").split(",")
                    left_power = float(both_data[0])
                    right_power = float(both_data[1])
                except Exception as e:
                    logger.error("TCE: App: Both Motor Error ->" + str(e))
                logger.info("App: BothMotor: Left:" + str(left_power) + ", Right: " + str(right_power))
                self.motor.left(left_power)
                self.motor.right(right_power)

            elif "servo" in str(received_data):
                # サーボ
                angle = 0.0
                try:
                    angle = float(str(received_data).replace("servo", ""))
                except Exception as e:
                    logger.error("TCE: App: Servo Error ->" + str(e))
                logger.info("App: Servo:" + str(angle))
                self.servo.angle(angle)

            elif "buzzer" in str(received_data):
                # ブザー
                freq = 0.0
                try:
                    freq = float(str(received_data).replace("buzzer", ""))
                except Exception as e:
                    logger.error("TCE: App: Buzzer Error ->" + str(e))
                logger.info("App: Buzzer:" + str(freq))
                self.buzzer.sound(freq)
                
            elif "updateVS" in str(received_data):
                # ビデオ設定
                height = 0
                width = 0
                frameRate = 0
                try:
                    all_data = str(received_data).replace("updateVS", "").split(",")
                    height = int(all_data[0])
                    width = int(all_data[1])
                    frameRate = int(all_data[2])
                    isAvailable = int(all_data[3])
                except Exception as e:
                    logger.error("TCE: App: Update vs Error ->" + str(e))
                logger.info("App: UpdateVS: height: " + str(height) + ", width: " + str(width) + ", frameRate: " + str(frameRate) + ", isAvailable: " + str(isAvailable))
                self.save_video_settings(height, width, frameRate, isAvailable)
                
            elif "led" in str(received_data):
                # LED ON
                n = 0
                r = 0
                g = 0
                b = 0
                try:
                    all_data = str(received_data).replace("led", "").split(",")
                    n = int(all_data[0])
                    r = int(all_data[1])
                    g = int(all_data[2])
                    b = int(all_data[3])
                    self.led.set(n, r, g, b)
                except Exception as e:
                    logger.error("TCE: App: Led  Error ->" + str(e))
                logger.info("App: Led: n: " + str(n) + ", r: " + str(r) + ", g: " + str(g) + ", b: " + str(b))

            elif "onFan" in str(received_data):
                # ファン起動
                logger.info("App: Fan on")
                self.fan.isForce = True
                self.fan.on()

            elif "offFan" in str(received_data):
                # ファン終了
                logger.info("App: Fan off")
                self.fan.isForce = True
                self.fan.off()

            elif "autoFan" in str(received_data):
                # ファンオートモード起動
                logger.info("App: Fan auto mode")
                self.fan.isForce = False
                self.fan.off()
                
    # カメラのビデオ設定を保存
    def save_video_settings(self, height, width, frameRate, isAvailable):
        import json

        # 保存するデータの準備
        data = {}
        data["height"] = height
        data["width"] = width
        data["frameRate"] = frameRate
        if isAvailable == 1:
            data["isAvailable"] = True
        else:
            data["isAvailable"] = False
        
        # データ保存
        logger.info("Saving Video Settings json")
        try:
            with open(self.main_dir + "sub/static/video_settings.json", "w")  as f:
                json.dump(data, f, ensure_ascii = False)
            logger.info("Restarting browser")
            self.browser.close_browser()
            subprocess.run("sudo systemctl restart raspberrypi.service", shell=True)
        except Exception as e:
            logger.error("TCE: Saving Video Settings json Error ->" + str(e))
            
    # SkyWay再起動時に実行される関数
    def skyway_restarted(self):
        self.skyway_connection_lost_count = -1
        
    # SkyWayの定期接続確認開始関数
    def skyway_connection_checker_start(self):
        self.skyway_connection_lost_count = -2
        self.skyWayConnectionCheck = False
        t2 = threading.Thread(target=self.skyway_connection_checker, args=[])
        t2.start()
    
    # SkyWayの定期接続確認関数
    def skyway_connection_checker(self):
        while True:
            if self.skyWayConnectionCheck == True:
                # 定期接続成功時
                logger.info("SkyWay Connection Checker: Success connection")
                self.skyWayConnectionCheck = False
                self.skyway_connection_lost_count = 2
                self.browser.isConnectChecked = True
            else:
                # 定期接続失敗時
                logger.info("SkyWay Connection Checker: Lost connection:" + str(self.skyway_connection_lost_count))
                self.skyway_connection_lost_count = self.skyway_connection_lost_count + 1
                self.motor.left(0.0)
                self.motor.right(0.0)
            
            # 失敗が一定数溜まった場合再起動
            if self.skyway_connection_lost_count >= 4:
                logger.info("SkyWay Connection Checker: Reloading skyway (reason: connection lost)")
                self.skyway_connection_lost_count = -2
                self.browser.reload_browser()
                self.browser.isConnectChecked = False
                
            time.sleep(5)
        

# このファイルが実行されたときの処理
if __name__ == "__main__":
    logger.info("Running main.py")
    try:
        main = Main()
    except Exception as e:
        logger.critical("TCE: Main Error -> " + str(e))