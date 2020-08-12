#/bin/bash
cd ~/darknet

sudo systemctl restart nvargus-daemon

#python3 ~/kickstart-jetson/darknet_video_advanced2.py --show_video t --video 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)1848, format=(string)NV12, framerate=(fraction)28/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx, width=(int)1920, height=(int)1080 !  videoconvert ! appsink sync=false  drop=true '

python3 ~/kickstart-jetson/darknet_video_advanced2.py --show_video t --video 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! appsink sync=false drop=true max-buffers=1'