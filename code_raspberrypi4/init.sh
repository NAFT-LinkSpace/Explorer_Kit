#!/bin/sh

#chmod 777 ./code_raspberrypi4/init.sh
#./code_raspberrypi4/init.sh

echo [Explorer Kit] Init Program Running 1.1 Creating log directory
mkdir code_raspberrypi4/log
echo [Explorer Kit] Init Program Running 1.2 Setting permission of log directory
sudo chmod 777 code_raspberrypi4/log

echo [Explorer Kit] Init Program Running 2.1 Setting camera
sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins gstreamer1.0-libcamera
echo [Explorer Kit] Init Program Running 2.2 Setting camera
sudo apt-get install -y v4l2loopback-dkms
echo [Explorer Kit] Init Program Running 2.3 Setting camera, creating file
sudo cp code_raspberrypi4/makefile/modules-load.d/v4l2loopback.conf /etc/modules-load.d
echo [Explorer Kit] Init Program Running 2.4 Setting camera, creating file
sudo cp code_raspberrypi4/makefile/modprobe.d/v4l2loopback.conf /etc/modprobe.d

# echo [Explorer Kit] Init Program Running 3.1 Installing pip libraries
# sudo pip install --break-system-packages -r code_raspberrypi4/requirements.txt
# echo [Explorer Kit] Init Program Running 3.2 Installing apt libraries
# sudo apt install chromium-chromedriver

# echo [Explorer Kit] Init Program Running 4.1 Updating apt
# sudo apt update
# echo [Explorer Kit] Init Program Running 4.2 Updating apt libraries
# sudo apt full-upgrade

echo [Explorer Kit] Init Program Running 5.1 Starting servo motor
sudo service pigpiod start
echo [Explorer Kit] Init Program Running 5.2 Enabling auto start servo motor
sudo systemctl enable pigpiod.service

echo [Explorer Kit] Init Program Running 6.1 Setting auto reboot on freeze, writing
sudo echo dtparam=watchdog=on >> /boot/firmware/config.txt
echo [Explorer Kit] Init Program Running 6.2 Setting auto reboot on freeze, creating directory
mkdir /etc/systemd/system.conf.d
echo [Explorer Kit] Init Program Running 6.3 Setting auto reboot on freeze, writing
sudo echo [Manager] >> /etc/systemd/system.conf.d/main.conf
echo [Explorer Kit] Init Program Running 6.4 Setting auto reboot on freeze, writing
sudo echo RuntimeWatchdogSec=5 >> /etc/systemd/system.conf.d/main.conf #正しい？
echo [Explorer Kit] Init Program Running 6.5 Setting auto reboot on freeze, writing
sudo echo options bcm2835_wdt heartbeat=10 nowayout=0 >> /etc/modprobe.d/bcm2835-wdt.conf

echo [Explorer Kit] Init Program Running 7.1 Setting auto startup program, creating file
sudo cp code_raspberrypi4/makefile/raspberrypi.service /etc/systemd/system
echo [Explorer Kit] Init Program Running 7.2 Enabling auto startup program
sudo systemctl enable raspberrypi.service #ここはお好みがよさそう?

# 全て終わったらREBOOT
