#/bin/bash
cd ~/darknet
python3 ~/kickstart-jetson/darknet_video_advanced.py --show_video t --video 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)1848, format=(string)NV12, framerate=(fraction)28/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx, width=(int)1280, height=(int)1080 !  videoconvert ! appsink sync=false async=false'
