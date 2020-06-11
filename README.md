
# Kickstart-Jetson
> Kickstart Jetson STEM Course
> Bootstraping the Jetson nano with Darknet Yolo

## Step 1. Clone my opensource repo
> This automatically do some magic stuffs
```bash
git clone https://github.com/samsonadmin/kickstart-jetson.git
cd kickstart-jetson
```

## Step 2. Configure network, make a hotspot for easy control
> Create Wi-Fi hotspot 
> you might need to change the code to change ssid and password
```bash
./configure-network.sh
```

|                |ascii                      
|----------------|-------------------------------
|SSID            |`i_am_jetson`          
|Password        |`jetsonnano`           


## Step 3. Install required software and libraries
```bash
./requirements.sh
```

## Step 4. Download Yolo

```bash
cd
git clone https://github.com/AlexeyAB/darknet.git
```

## Step 5. Edit Makefile
```bash
vim Makefile
```
```diff
GPU=1
CUDNN=1
OPENCV=1
OPENMP=1
```
```diff
#uncomment the line
ARCH= -gencode arch=compute_53,code=[sm_53,compute_53]
```

## Step 6. Compile the program
```bash
make -j4
```

## Step 7. Download models & weights 
```bash
#model
wget http://www.mail2you.net/weights/yolo_v3_tiny_pan3_aa_ae_mixup_scale_giou_dropblock_mosaic.cfg.txt
#weights
wget http://www.mail2you.net/weights/yolov3-tiny.conv.11

#model
wget https://raw.githubusercontent.com/WongKinYiu/PartialResidualNetworks/master/cfg/yolov3-tiny-prn.cfg
#weights
wget http://www.mail2you.net/weights/yolov3-tiny.weights

#model
wget http://www.mail2you.net/weights/yolov3-tiny-prn.cfg
#weights
wget http://www.mail2you.net/weights/yolov3-tiny-prn.weights
```

## Step 8. Your first inference!
```bash
./darknet detector test cfg/coco.data yolov3-tiny-prn.cfg yolov3-tiny-prn.weights data/person.jpg
```

## Step 9. Lets test on video
```bash
./darknet detector test cfg/coco.data yolov3-tiny-prn.cfg yolov3-tiny-prn.weights data/person.jpg
```

## Step 10. Take Pictures and build your own training
> Let's take some time and allow me to explain what are the important things you need to consider when doing your training
> 

## Step 11. Train your weight
> However, training is almost impossible to be done on jetson nano, lets do it on cloud, we will use [Google Colab](https://colab.research.google.com/drive/1lfcAim-fHge2L9fdD49eu8LNUaAMgk4G?usp=sharing)
```bash
 ./darknet detector train "/training-data/face_mask/obj-google.data"  "/training-data/face_mask/yolov3-tiny-prn-832.cfg"  "/training-data/face_mask/yolov3-tiny-prn-832_last.weights" -dont_show
 ```


----
----
# Other useful scripts

## GPIO
See [https://www.jetsonhacks.com/2019/06/07/jetson-nano-gpio/](https://www.jetsonhacks.com/2019/06/07/jetson-nano-gpio/)
See [https://github.com/NVIDIA/jetson-gpio](https://github.com/NVIDIA/jetson-gpio)


```bash
sudo -H pip3 install Jetson.GPIO luma.led_matrix

sudo groupadd -f -r gpio
sudo usermod -a -G gpio your_user_name
sudo usermod -a -G gpio jetsonnano

sudo cp /lib/udev/rules.d/60-jetson-gpio-common.rules  /etc/udev/rules.d/
sudo reboot
```

https://forums.developer.nvidia.com/t/read-write-permission-ttyths1/81623

created a udev rule: /etc/udev/rules.d/55-tegraserial.rules
KERNEL=="ttyTHS*", MODE="0666"
```bash
sudo /etc/rc.local
chmod 666 /dev/ttyTHS1
```


## Enable SPI on jetson nano

https://github.com/gtjoseph/jetson-nano-support/tree/l4t_32.2.1


## For SPI, https://github.com/gtjoseph/jetson-nano-support/tree/master

```bash
wget https://github.com/gtjoseph/jetson-nano-support/releases/download/v1.0.2/flash-dtb-update-2019-12-09.tar.gz
tar -zxvf flash-dtb-update-2019-12-09.tar.gz
```


## Using the max7219 matrix LED
```bash
pip install luma.led_matrix
```

### hardware:
https://raspi.tv/2013/8-x-8-led-array-driven-by-max7219-on-the-raspberry-pi-via-python

### Software:
https://github.com/rm-hull/luma.led_matrix


## Manage Autostart


Using Linux  **rc.local**
https://www.linuxbabe.com/linux-server/how-to-enable-etcrc-local-with-systemd
https://vpsfix.com/community/server-administration/no-etc-rc-local-file-on-ubuntu-18-04-heres-what-to-do/
```bash
sudo vim /etc/rc.local
#allow sending serial
if [ -f "/dev/ttyTHS1" ]; then
        chmod 666 /dev/ttyTHS1
fi

if [ -f "/dev/ttyUSB0" ]; then
        chmod 666 /dev/ttyUSB0
fi
```

# Finally
```bash
./start.sh
```
