# #coding:utf-8

# 要修正
# 公開前に下のコメントアウト消去

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import time
import subprocess

class LED:
    # 初期化
    def __init__(self):
        self.intervalCount = 0
        self.isAvailable = True
        
    # 指定されたLEDを指定された色に光らせる
    def set(self, n, g, r, b):
        # subprocess.run("sudo /usr/bin/python /home/naft/Desktop/NCS_2024_Explorer_Kit/code_raspberrypi4/sub/led_sudo.py 0a0a255a255", shell=True)
        
        args = ["sudo", "/usr/bin/python", "/home/naft/Desktop/NCS_2024_Explorer_Kit/code_raspberrypi4/sub/led_sudo.py"]

        args.append(str(n))
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))

        subprocess.Popen(args)
    
    # 現在のステータス表示用(使用されていない)
    def set_status(self, n):
        if n == 0:
            # 通常運転
            if self.intervalCount % 2 == 0:
                self.set(0, 0, 150, 0)
            else:
                self.set(0, 0, 100, 0)
            self.intervalCount = self.intervalCount + 1
        elif n == 1:
            # 未接続状態（再起動）
            if self.intervalCount % 2 == 0:
                self.set(0, 150, 0, 150)
            else:
                self.set(0, 100, 0, 50)
            self.intervalCount = self.intervalCount + 1
        elif n == 2:
            # 未接続状態（googleチェッカー）
            if self.intervalCount % 2 == 0:
                self.set(0, 150, 150, 150)
            else:
                self.set(0, 100, 50, 50)
            self.intervalCount = self.intervalCount + 1
        elif n == 3:
            # エラー発生
            self.set(0, 150, 0, 0)
        elif n == 4:
            # 終了
            self.set(0, 0, 0, 0)
        elif n == 4:
            # 再起動開始
            self.set(0, 150, 150, 0)
            
    

# このファイルが実行されたときの処理
if __name__ == "__main__":
    led = LED()
    led.set(0, 150, 0, 0)