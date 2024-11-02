# app.py

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

# 送受信したデータをmainに保存するため
main = None

logger.info("Starting Flask apppy")

@app.route('/')
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "video_settings.json")
    data = json.load(open(json_url))
    return render_template('index.html', jdata=data)

@app.route("/flask")
def flask():
    return render_template("flask.js")

# データを受信した際に実行される関数
@app.route('/execute', methods=['GET', 'POST'])
def execute():
    # データをSkyWayに送信する（JSから関数loop）
    if request.method == 'GET':
        logger.info("GET")
        
        # 送るデータが準備できるまで待機
        x = 0
        while len(main.send_data_list) == 0:
            x = x + 1
            
        # 送るデータを選び、そのデータを待ち列から削除
        data = main.send_data_list[0]
        main.send_data_list.remove(data)
        
        # データ送信
        return json.dumps(data)
    
    # データをSkyWayから受信する
    if request.method == 'POST':
        logger.info("POST")
        
        # 受信したデータを変数に代入
        received_data = request.form['received_data']
        
        # 受信したデータをmain.pyに送り非同期変換
        main.data_received_async(received_data)
        
        return json.dumps({"Success": True})
        

if __name__ == '__main__':
    print("main.pyから実行してください")