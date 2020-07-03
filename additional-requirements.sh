#!/bin/bash
sudo -H pip3 install -U pip

#sudo -H pip3 install scikit-image

#sudo -H pip3 install adafruit-circuitpython-ssd1306 luma.oled
#sudo apt-get install python3-pil

#pip3 install adafruit-blinka


i2cdetect -y -r 1

cd
cd darknet
wget http://www.mail2you.net/weights/yolov4-tiny.weights

