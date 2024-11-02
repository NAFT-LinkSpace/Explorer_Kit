#coding: utf-8

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

class Browser:
    
    # 初期化
    def __init__(self):
        self.isConnectChecked = False
        self.driver_path = '/usr/bin/chromedriver'
        self.options = Options()
        
        # カメラを自動で許可
        self.options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        self.options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.media_stream_camera': 1, # 1:allow, 2:block 
            })
        
        # Chrome起動
        self.service = Service(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(options=self.options, service=self.service)
    
    # 一度ウィンドウを縮小し、再度拡大する関数
    def switch_window(self):
        self.driver.minimize_window()
        time.sleep(3)
        self.driver.maximize_window()
        
    # Flaskのサイトにアクセスする関数
    def open_browser(self):
        self.driver.get("http://127.0.0.1:5000/")
    
    # Chromeを終了する関数
    def close_browser(self):
        self.driver.quit()
    
    # ブラウザを再起動する関数
    def reload_browser(self):
        if self.isConnectChecked == True:
            # 一度通信が途切れたらブラウザごと再起動
            self.close_browser()
            time.sleep(3)
            self.driver = webdriver.Chrome(options=self.options, service=self.service)
            self.open_browser()
        else:
            # サイトを再読み込みする
            self.driver.refresh()