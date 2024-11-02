#coding: utf-8

# 参考文献
# gangan: 【メモ】ラズパイのCPU使用率をPythonで測定する
# https://gangannikki.hatenadiary.jp/entry/2020/10/15/200000

# loggerの設定
import logging
logger = logging.getLogger("メインログ")

import time
import subprocess
import sys
import psutil

class CPU:
    
    # CPU周波数取得関数
    def GetCpuFreq(self):
        Cmd = "vcgencmd measure_clock arm"
        res = subprocess.Popen(Cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
        Rstdout, Rstderr = res.communicate()
        CpuFreq = Rstdout.split("=")
    
        CpuFreq_str = "{:4d}".format(int(int(CpuFreq[1]) / 1000000)) # MHzに変換
    
        return int(CpuFreq_str)
    
    # CPU温度取得関数
    def GetCpuTemp(self):
        Cmd = "vcgencmd measure_temp"
        res = subprocess.Popen(Cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
        Rstdout, Rstderr = res.communicate()
        Cputemp = Rstdout.split()
    
        Cputemp_str = Cputemp[0].split("=")[1].split("'")[0]
    
        return float(Cputemp_str)
    
    # CPUステータス取得関数
    def GetCpuStat(self):
        Cmd = "cat /proc/stat | grep cpu"
        res = subprocess.Popen(Cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
        Rstdout,Rstderr = res.communicate()
        #  行ごとに分割
        LineList = Rstdout.splitlines()
    
        usageList = []
    
        Tcklist = []
        for line in LineList:
            ItemList = line.split()
            Idle = int(ItemList[4])
            Busy = int(ItemList[1]) + int(ItemList[2]) + int(ItemList[3])
            All = Busy + Idle
            Tcklist.append([ Busy, All ])
            usageList.append(int(Busy * 100 / All))
            
        return usageList
    
    # CPUやメモリに関するデータを取得する関数
    def getData(self):
        
        # main.pyで使用するデータに変換
        main_data = {}
    
        main_data["status"] = True
        main_data["freq"] = self.GetCpuFreq()
        main_data["temp"] = self.GetCpuTemp()
        main_data["stat"] = self.GetCpuStat()
    
        main_data["memper"] = psutil.virtual_memory().percent
        main_data["memnow"] = psutil.virtual_memory().used / (1024 * 1024 * 1024)
        main_data["memmax"] = psutil.virtual_memory().total / (1024 * 1024 * 1024)
    
        return main_data

# このファイルが実行されたときの処理
if __name__ == "__main__":
    cpu = CPU()
    while True:
        x_data = cpu.getData()
        print(x_data)
        time.sleep(1)
        