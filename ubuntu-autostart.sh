#/bin/bash
cd ~/darknet
export DISPLAY=:0

echo "If failed, run below command:"
echo "sudo systemctl restart nvargus-daemon"

python3 ~/kickstart-jetson/darknet_video_advanced.py --show_video t --video 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! appsink sync=false drop=true max-buffers=1'

