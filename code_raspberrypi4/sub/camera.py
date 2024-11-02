#coding: utf-8

# 画像認識用のコード

# 参考文献
# Yuzu2yan: 【色検知】OpenCVで色情報から特定の物体を検出してみる
# https://qiita.com/Yuzu2yan/items/056778f2707d6931519e

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

class Camera:
    
    # 初期化
    def __init__(self):
      
      # Chromeで出力された映像を使えるようにする
      # ここでの画像サイズ、FPSがSkyWayに送信される最大値！
      self.out = cv2.VideoWriter(
        'appsrc ! videoconvert ! videoscale ! video/x-raw,format=I420 ! v4l2sink device=/dev/video8',
        0,           # 出力形式。今回は0で。
        10,          # FPS
        (640, 480),  # 出力画像サイズ
        )
      
      # 赤色は２つの領域にまたがります！！
      # np.array([色彩, 彩度, 明度])
      # 各値は適宜設定する！！
      self.LOW_COLOR1 = np.array([0, 50, 50]) # 各最小値を指定
      self.HIGH_COLOR1 = np.array([6, 255, 255]) # 各最大値を指定
      self.LOW_COLOR2 = np.array([174, 50, 50])
      self.HIGH_COLOR2 = np.array([180, 255, 255])
      self.picam2 = Picamera2()
      self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
      self.picam2.start()
      #カメラを連続オートフォーカスモードにする
      self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    
    # 画像認識を開始する
    def start(self):
      
      while True:
        img = self.picam2.capture_array()
        img_after = img
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV) # RGB => YUV(YCbCr)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)) # claheオブジェクトを生成
        img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0]) # 輝度にのみヒストグラム平坦化
        img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR) # YUV => RGB
        img_blur = cv2.blur(img, (15, 15)) # 平滑化フィルタを適用
        hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV) # BGRからHSVに変換
        bin_img1 = cv2.inRange(hsv, self.LOW_COLOR1, self.HIGH_COLOR1) # マスクを作成
        bin_img2 = cv2.inRange(hsv, self.LOW_COLOR2, self.HIGH_COLOR2)
        mask = bin_img1 + bin_img2 # 必要ならマスクを足し合わせる
        masked_img = cv2.bitwise_and(img_blur, img_blur, mask= mask) # 元画像から特定の色を抽出
        out_img = masked_img
        num_labels, label_img, stats, centroids = cv2.connectedComponentsWithStats(mask) # 連結成分でラベリングする
        # 背景のラベルを削除
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        centroids = np.delete(centroids, 0, 0)
        if num_labels >= 1: # ラベルの有無で場合分け
          logger.debug("Camera: Found target!!")
          max_index = np.argmax(stats[:, 4]) # 最大面積のインデックスを取り出す
          # 以下最大面積のラベルについて考える
          x = stats[max_index][0]
          y = stats[max_index][1]
          w = stats[max_index][2]
          h = stats[max_index][3]
          s = stats[max_index][4]
          mx = int(centroids[max_index][0]) # 重心のX座標
          my = int(centroids[max_index][1]) # 重心のY座標
          cv2.rectangle(img_after, (x, y), (x+w, y+h), (255, 0, 255), 4) # ラベルを四角で囲む
          cv2.putText(img_after, "%d,%d"%(mx, my), (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0)) # 重心を表示
          cv2.putText(img_after, "%d"%(s), (x, y+h+30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0)) # 面積を表示
        else:
          logger.debug("Camera: No target!!")
        #   cv2.imshow("Camera", img_after)
        img_yuv_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2YUV) # RGB => YUV(YCbCr)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)) # claheオブジェクトを生成
        img_yuv_after[:,:,0] = clahe.apply(img_yuv_after[:,:,0]) # 輝度にのみヒストグラム平坦化
        img_after = cv2.cvtColor(img_yuv_after, cv2.COLOR_YUV2BGR) # YUV => RGB
        self.out.write(img_after)
        
# このファイルが実行されたときの処理
if __name__ == "__main__":
  camera = Camera()
  camera.start()