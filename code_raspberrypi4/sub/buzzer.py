#coding: utf-8

# 参考文献
# nokomilk_fish: 【初心者向け】圧電スピーカーで音を鳴らそう｜ラズパイで電子工作
# https://qiita.com/nokomilk_fish/items/5bb715534d7473de37b1

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

from gpiozero import TonalBuzzer
import time
import math

class Buzzer:
    
    # 初期化
    def __init__(self):
        pin = 24 # ブザーのGPIO
        self.bz = TonalBuzzer(pin)
        
    # 指定した周波数で音を鳴らす関数
    def sound(self, freq):
        self.bz.play(freq)
        time.sleep(3)
        self.bz.stop()
    
    def music(self):
        
        #それぞれの音の周波数を定義
        DO="C5"
        RE="D5"
        MI="E5"
        SO="G5"

        #メロディとリズムを配列に
        mery_merody=[MI,RE,DO,RE,MI,MI,MI,RE,RE,RE,MI,SO,SO,MI,RE,DO,RE,MI,MI,MI,RE,RE,MI,RE,DO]
        mery_rhythm=[0.9,0.3,0.6,0.6,0.6,0.6,1.2,0.6,0.6,1.2,0.6,0.6,1.2,0.9,0.3,0.6,0.6,0.6,0.6,1.2,0.6,0.6,0.9,0.3,1.8]

        #配列の通りに鳴らす
        for i, oto in enumerate(mery_merody):
            self.bz.play(oto)
            time.sleep(mery_rhythm[i])
            self.bz.stop()
            time.sleep(0.03)

# このファイルが実行されたときの処理
if __name__ == "__main__":
    buzzer = Buzzer()
    buzzer.music()
