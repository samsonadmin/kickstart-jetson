
#gst-launch-1.0 -e -v v4l2src device=/dev/video0 io-mode=2 do-timestamp=true ! image/jpeg, width=1920, height=1080, framerate=30/1 ! jpegparse ! nvjpegdec ! 'video/x-raw(memory:NVMM)' !  nvvidconv ! 'video/x-raw(memory:NVMM),format=I420,width=1920,height=1080' ! \

#  rtmpsink location 'rtmp://192.168.1.10:1935/live/test'

#	nvoverlaysink sync=false



#works on vlc/potplayer/web player
#rtmp://192.168.1.10/live/demo2


#gst-launch-1.0 -v v4l2src io-mode=2 device='/dev/video0' ! 'video/x-raw, format=(string)YUY2, width=(int)1920, height=(int)1080, framerate=(fraction)60/1' !  nvvidconv ! nvv4l2h264enc control-rate=1 bitrate=30000000 preset-level=4 profile=4 ! h264parse ! flvmux  ! rtmpsink location='rtmp://192.168.1.10/live/demo2' -e



#gst-launch-1.0 -v videotestsrc ! nvvidconv ! nvv4l2h264enc ! h264parse ! flvmux  ! rtmpsink location='rtmp://192.168.1.10/live/demo2' -e


#http://192.168.1.10:8080/hls/demo2.m3u8

gst-launch-1.0 -v v4l2src io-mode=2 device='/dev/video0' ! 'video/x-raw, format=(string)YUY2, width=(int)1920, height=(int)1080, framerate=(fraction)60/1' !  nvvidconv ! nvv4l2h264enc control-rate=1 bitrate=10000000 preset-level=4 profile=4 ! h264parse ! flvmux  ! rtmpsink location='rtmp://192.168.1.10/hls/demo2' -e