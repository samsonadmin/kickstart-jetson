#/bin/bash
cd ~/darknet
export DISPLAY=:0

echo "If failed, run below command:"
echo "sudo systemctl restart nvargus-daemon"

python3 ~/kickstart-jetson/darknet_video_advanced.py --show_video t --video 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! appsink sync=false drop=true max-buffers=1'


#python3 ~/kickstart-jetson/darknet_video_advanced.py --show_video t --video \
'v4l2src io-mode=2 device=/dev/video0 ! image/jpeg, width=1280, height=720, framerate=30/1 ! jpegdec ! video/x-raw ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)I420 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink max-buffers=1 drop=true sync=false'