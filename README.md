

# Kickstart-Jetson
> Kickstart Jetson STEM Course
> Bootstraping the Jetson nano with Darknet Yolo

## Step 0. Download the image for NVIDIA Jetson (already prepared for you) 
Jetson Nano Developer Kit SD Card Image [https://developer.nvidia.com/embedded/downloads](https://developer.nvidia.com/embedded/downloads)
and burn ISO using [balenaEtcher](https://www.balena.io/etcher/)

## Step 1. Insert SD Card, connect Camera, fan, etc
> boot up the Jetson nano
> Ensure the *JP48* is connected, connect the 5V 4A power

## Step 2. Clone my opensource repo
> This automatically do some magic stuffs
```bash
git clone https://github.com/carryai/kickstart-jetson.git
cd kickstart-jetson
```

## Step 3. Configure network, make a hotspot for easy control
> Create Wi-Fi hotspot 
> you might need to change the code to change ssid and password
```bash
./configure-network.sh
```

|                |ascii                      
|----------------|-------------------------------
|SSID            |`i_am_jetson`          
|Password        |`jetsonnano`           


## Step 4. Install required software and libraries
```bash
./requirements.sh
```

## Step 5. Back to your computer, prepare Visual Studio Code

![Visual Studio Code](https://www.mail2you.net/stem/vcs01.jpg)

![Visual Studio Code](https://www.mail2you.net/stem/vcs02.jpg)

![Visual Studio Code](https://www.mail2you.net/stem/vcs03.jpg)
>c:\Users\**(your_username)**\.ssh\config
```bash
Host Jetsonnano-192.168.2.1
	HostName 192.168.2.1
	User jetsonnano
	ForwardAgent yes
	StrictHostKeyChecking no
```

![Visual Studio Code](https://www.mail2you.net/stem/vcs04.jpg)

![Visual Studio Code](https://www.mail2you.net/stem/vcs05.jpg)


![Visual Studio Code](https://www.mail2you.net/stem/vcs06.jpg)

![Visual Studio Code](https://www.mail2you.net/stem/vcs07.jpg)


## Step 6. Download Yolo

```bash
cd
git clone https://github.com/AlexeyAB/darknet.git
```

## Step 7. Edit Makefile
```bash
nano Makefile
```


## Change the following contents of the Makefile
```diff
GPU=1
CUDNN=1
OPENCV=1
LIBSO=1
```

## Change the following contents of the Makefile, uncomment the lines
```diff
#uncomment the line
ARCH= -gencode arch=compute_53,code=[sm_53,compute_53]
```

## Change the the environment file, ~/.bashrc
```bash
nano ~/.bashrc
```

## add the following into the end of ~/.bashrc
```bash
export CUDA_VER=10.0
export PATH=${PATH}:/usr/local/cuda/bin
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/cuda/lib64
```

## activate ~/.bashrc
```bash
source ~/.bashrc
```

## Step 8. Compile the program
```bash
make -j4
```

## Step 9. Download models & weights 
cd ~/darknet
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights -O yolov4-tiny.weights

wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-csp.weights -O yolov4-csp.weights

## Step 10. Your first inference!
```bash
./darknet detector test ~/darknet/cfg/coco.data ~/darknet/cfg/yolov4-csp.cfg ~/darknet/yolov4-csp.weights data/person.jpg
```

## Step 11. Lets test with USB Camera
```bash
cd ~/darknet
export DISPLAY=:1

./darknet detector demo  ~/darknet/cfg/coco.data  ~/darknet/cfg/yolov4-csp.cfg   ~/darknet/yolov4-csp.weights    -thresh 0.50 -ext_output \
'v4l2src io-mode=2 device=/dev/video0 ! image/jpeg, width=1920, height=1080, framerate=30/1 ! jpegdec ! video/x-raw !  nvvidconv ! video/x-raw(memory:NVMM), format=(string)I420 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink max-buffers=1 drop=true sync=false'  


```

## Step 12. Take Pictures and build your own training
> Let's take some time and allow me to explain what are the important things you need to consider when doing your training
> 

## Step 13. Train your weight
> However, training is almost impossible to be done on jetson nano, lets do it on cloud, we will use [Google Colab](https://colab.research.google.com/drive/1czTxmIIcMkqRdgbsTOOmO4ecBeFIrKP8)
```bash
 ./darknet detector train "/training-data/face_mask/obj-google.data"  "/training-data/face_mask/yolov3-tiny-prn-832.cfg"  "/training-data/face_mask/yolov3-tiny-prn-832_last.weights" -dont_show
 ```


----
----
# Other useful scripts

## GPIO
See [https://www.jetsonhacks.com/2019/06/07/jetson-nano-gpio/](https://www.jetsonhacks.com/2019/06/07/jetson-nano-gpio/)
See [https://github.com/NVIDIA/jetson-gpio](https://github.com/NVIDIA/jetson-gpio)

##　Running Jetson-IO
After the setup, we’re ready to go:
```bash
sudo /opt/nvidia/jetson-io/jetson-io.py
 ```
 ![Visual Studio Code](https://i0.wp.com/www.jetsonhacks.com/wp-content/uploads/2020/05/JetsonIO-Main.png?w=635&ssl=1)
 


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

## Jetson Nano 3D printer samples
https://www.thingiverse.com/thing:3603594
https://www.thingiverse.com/thing:4082134
https://www.prusaprinters.org/prints/4689-jetson-nano-case
https://www.prusaprinters.org/prints/1420-nvidia-jetson-nano-case-nanomesh-mini

# Finally
```bash
./start.sh
```

# Save as a copy in Drive
https://colab.research.google.com/drive/1czTxmIIcMkqRdgbsTOOmO4ecBeFIrKP8



# Connections
[How to connect](CONNECTION-README.md)

# If you find that the image captured is red. You can try to download .isp file and installed:
https://www.waveshare.com/wiki/IMX219-160_Camera

```bash
wget https://www.waveshare.com/w/upload/e/eb/Camera_overrides.tar.gz
tar zxvf Camera_overrides.tar.gz 
sudo cp camera_overrides.isp /var/nvidia/nvcam/settings/
sudo chmod 664 /var/nvidia/nvcam/settings/camera_overrides.isp
sudo chown root:root /var/nvidia/nvcam/settings/camera_overrides.isp
rm Camera_overrides.tar.gz 
rm camera_overrides.isp
```
