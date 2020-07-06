#!/bin/bash

#works
#please make sure
#sudo apt-get install -y v4l-utils
#https://github.com/umlaeute/v4l2loopback
#sudo modprobe v4l2loopback video_nr=8,9  card_label="Virtual Video Sink 8","Virtual Video Sink 9"  buffers=1
#gst-launch-1.0 -v videotestsrc ! video/x-raw, width=1920, height=1080, format=BGRx ! v4l2sink device=/dev/video9
#gst-launch-1.0 v4l2src device=/dev/video9 ! videoconvert ! ximagesink
#sudo modprobe -r v4l2loopback

#gst-launch-1.0 v4l2src device=/dev/video0 ! "video/x-raw,width=1920,height=1080,framerate=30/1" ! tee name=rec ! queue ! v4l2sink device=/dev/video8 rec. ! queue ! v4l2sink device=/dev/video9


declare -A VIDEO_CAMERA_INPUTS
declare -A yolo_detection_options

myIPAddress=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | tr '\n' '|' )
myIPAddress=${myIPAddress::-1}

v4l2src_pipeline_str=""
v4l2src_ending_pipeline_str=""
nvvidconv_flip=""
resize_to_resolution="N/A"
video_file_for_v4l2src_pipeline=""

test_videos_dir="/home/jetsonnano/test-videos"

#map it to HDMI output
export DISPLAY=:0
#if this doesn't work,
#export DISPLAY=:1.0


#today=`date +%Y-%m-%d.%H:%M:%S`
today=`date +%Y%m%d-%H%M%S`

yolo_detection_options[0,0]="Mask (Require GUI X11)"
yolo_detection_options[0,1]="~/darknet/mask/obj.edge.data"
yolo_detection_options[0,2]="~/darknet/mask/yolov4-tiny.cfg"
yolo_detection_options[0,3]="~/darknet/mask/yolov4-tiny_last.weights"
yolo_detection_options[0,4]="-thresh 0.80 -ext_output "


yolo_detection_options[1,0]="Yolov4 - Tiny Different objects (Require GUI X11)"
yolo_detection_options[1,1]="~/darknet/cfg/coco.data"
yolo_detection_options[1,2]="~/darknet/cfg/yolov4-tiny.cfg"
yolo_detection_options[1,3]="~/darknet/yolov4-tiny.weights"
yolo_detection_options[1,4]="-thresh 0.60 -ext_output "


#pause
clear

display_usage_help()
{
printf "Usages \n"
printf "./select-camera.sh start :::: Auto detect resource and restart, log file: restart-log.log\n"
printf "./select-camera.sh once :::: Auto start, without restart\n"
printf "./select-camera.sh stop :::: stop and quit loop\n"
printf "once defaults to /dev/video0\n\n"
}


nvvidconv_flip=""

pause()
{
	read -n1 -r -p "Press any key to continue..." key
	case $key in
		 $'\e')
		 printf "\n(Escape key)\n"
		 printf "v4l2src_pipeline_str:\n$v4l2src_pipeline_str\n\n"
		 exit 0	
		 ;;
	esac

}

kill_darknet()
{

	##Actual check
	darknet_pid=$(pgrep darknet)

	if [ "$darknet_pid" == "" ]; then
		##darknet not running, need to run again
		echo "Darknet not running"
	else
		sudo pgrep darknet | xargs sudo kill -9
	fi

}


kill_darknet_slient()
{

	##Actual check
	darknet_pid=$(pgrep darknet)

	if [ "$darknet_pid" != "" ]; then
		sudo pgrep darknet | xargs sudo kill -9
	fi

}




###################
#Detects if there are arguments from the command line
###################

autorun=false;
if [ "$1" == "once" ]; then
	autorun=true
fi

quit_darknet=false;
if [ "$1" == "stop" ]; then
	quit_darknet=true
	kill_darknet
	killall select-camera.sh
	exit 0
fi

if [ "$1" == "start" ]; then
	loop
	exit 0
fi

if [ "$1" == "--video-path" ]; then
	if [[ -d "$2" ]]; then
		test_videos_dir=$2
	else
		echo "Directory: $2 is not valid"
		exit 0
	fi
fi

if [ "$1" == "--help" ]; then
	echo "--video-path path	:For using the videos from the path (e.g. --video-path `pwd`)"
	echo "once	:Auto start Yolo with video0, don't auto-restart"
	echo "start	:Auto start and detect if error and auto-restart"
	exit 0
fi

###################
#show info function
###################
show_device_info()
{

			dpkg-query --show nvidia-l4t-core

			printf "compare latest version with: https://developer.nvidia.com/embedded/linux-tegra-archive\n";

			sudo nmcli device
			sudo nmcli con			
			sudo lsusb 

}



###################
#Show camera selection dialog
###################
show_menu_camera_selection()
{


	unset dialog_menu
	dialog_menu=()
	tmp_str=""

	#echo ${video_camera_array[@]}

	for (( i=0; i<${#video_camera_array[@]}; i++ ));
	do

		#echo "Name:	${VIDEO_CAMERA_INPUTS[$i,1]}"
		#echo "Type:	${VIDEO_CAMERA_INPUTS[$i,2]}"
		#echo ${VIDEO_CAMERA_INPUTS[$i,3]}
		#echo ${VIDEO_CAMERA_INPUTS[$i,4]}
		#echo "Width:	${VIDEO_CAMERA_INPUTS[$i,5]}"
		#echo "Height:	${VIDEO_CAMERA_INPUTS[$i,6]}"
		#echo "FPS:	${VIDEO_CAMERA_INPUTS[$i,7]}"

		tmp_str="(${VIDEO_CAMERA_INPUTS[$i,0]} ${VIDEO_CAMERA_INPUTS[$i,2]}) ${VIDEO_CAMERA_INPUTS[$i,5]}x${VIDEO_CAMERA_INPUTS[$i,6]}@${VIDEO_CAMERA_INPUTS[$i,7]}fps - ${VIDEO_CAMERA_INPUTS[$i,1]} "

		dialog_menu+=($i)
		dialog_menu+=($tmp_str)
		#dialog_menu+=("")

	done



	dialog_menu+=("k")
	dialog_menu+=("Kill Interference")
	dialog_menu+=("q")
	dialog_menu+=("Quit")
	dialog_menu+=("o")
	dialog_menu+=("Advanced Options")

	
	#Looping videos in from the folder $test_videos_dir
	IFS=$'\n\r'
	readarray -t test_videos < <(find "$test_videos_dir" -name "*.mp4" ! -path "*/archive/*" )
	for (( i=0; i<${#test_videos[*]}; i++ ));
	do
		dialog_menu+=("V${i}")
		this_video="${test_videos[$i]}"
		dialog_menu+=("${this_video##*/}")
	done

	return_str=$(whiptail --backtitle "Listing all the UVC Cameras" \
										--title "Select the video device" \
										--menu "/dev/video*" 16 78 8  \
										"${dialog_menu[@]}" 3>&1 1>&2 2>&3)

	#echo $return_str
	#pause
	camera_num=$(echo $return_str | rev | cut -b -1 )

	if [ "$return_str" != "" ]; then
		if [ $(echo $return_str | head -c 1)  == "V" ]; then
			test_video_index=${return_str:1}
			video_file_for_v4l2src_pipeline="${test_videos[$test_video_index]}"
		fi
	fi
		
	build_pipeline

	case $return_str in

		"k")
			kill_darknet
			show_menu_camera_selection
		;;
		

		"q")
			printf "\nQuit\n"
			exit 0
		;;
		
		"o")
			show_menu_advanced_options
		;;

		"")
			printf "\n(Escape key)\n"
			exit 0
		;;

		*)
			show_menu_camera_functions_lv1
		;;

	esac


}


##"02" "Image rotate 180" \


###################
#Advanced Options menu
###################
show_menu_advanced_options()
{

	back_title="Chosen Camera: ${VIDEO_CAMERA_INPUTS[$camera_num,1]} ${VIDEO_CAMERA_INPUTS[$camera_num,0]} ${VIDEO_CAMERA_INPUTS[$camera_num,5]}x${VIDEO_CAMERA_INPUTS[$camera_num,6]}@${VIDEO_CAMERA_INPUTS[$camera_num,7]}fps"

	current_power_mode=$(sudo nvpmodel -q | awk '/NV Power Mode/ {print $4}')

	function_selection=$(whiptail --backtitle "${back_title}" \
										--title "Advanced Options" \
										--menu "Select the below functions" 25 78 14 \
										"00" "Rotate Camera 180 (Current:${nvvidconv_flip})" \
										"01" "Resize the source (Current:${resize_to_resolution})" \
										"02" "Toggle Power Mode(Current: ${current_power_mode})" \
										"04" "Network Configurator" \
										"05" "Reset onboard camera with nvargus-daemon" \
										"06" "Show info" \
										"07" "Show camera" \
										"08" "Reboot" \
										"09" "Shutdown" 3>&1 1>&2 2>&3)


	##function_selection=$(echo $return_str | cut -b 1 )

	case $function_selection in

		00)
			clear
			if [[ $nvvidconv_flip == "" ]]; then
				nvvidconv_flip="flip-method=2 "
			else	
				nvvidconv_flip=""
			fi
	
			printf "Rotate camera by 180degree: $nvvidconv_flip\n";

			#pause
			
		;;



		01)
			clear
			case $resize_to_resolution in
				"N/A")
					resize_to_resolution="1280x720"
				;;
				"1280x720")
					resize_to_resolution="640x360"
				;;
				"640x360")
					resize_to_resolution="N/A"
				;;
			esac
			show_menu_advanced_options
		;;

		02)
			clear
			if [[ $( sudo nvpmodel -q | awk '/[0-9]+$/ {print $1}') == 0 ]]; then
				sudo nvpmodel -m 1
				sudo sh -c "echo -1 > /sys/module/usbcore/parameters/autosuspend"
				printf "\nSet to 5W successfully\n"
			else	
				#MAXN
				sudo nvpmodel -m 0

				sudo sh -c "echo -1 > /sys/module/usbcore/parameters/autosuspend"
				sudo sh -c "echo 1 > /sys/devices/system/cpu/cpu0/online"
				sudo sh -c "echo 1 > /sys/devices/system/cpu/cpu1/online"
				sudo sh -c "echo 1 > /sys/devices/system/cpu/cpu2/online"
				sudo sh -c "echo 1 > /sys/devices/system/cpu/cpu3/online"
				sudo sh -c "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
				sudo sh -c "echo performance > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor"
				sudo sh -c "echo performance > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor"
				sudo sh -c "echo performance > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor"
				printf "\nSet to 10W successfully\n"
								
			fi
	
			sudo nvpmodel -q
			
			printf "No of CPU: $(grep -c ^processor /proc/cpuinfo)\n";
			#pause
			show_menu_advanced_options
		;;



		04)
			clear
			sudo nmtui 

			pause
		;;


		05)
			clear
			sudo systemctl restart nvargus-daemon
	
			printf "systemctl restart nvargus-daemon\n";

			pause
		;;





		06)
			clear

			show_device_info
			pause

			printf "IP: $myIPAddress\n";

			sudo python3 info.py
			printf "Screen updated\n";
			
			pause
		;;


		07)
			printf "Doing: v4l2-ctl --device=$d -D --list-formats-ext \n"
			clear

			for d in /dev/video* ; do echo $d ; v4l2-ctl --device=$d -D --list-formats-ext  ; echo '===============' ; done

			pause
		;;


		08)
			clear
			printf "Reboot in 2s\n";
			sleep 2
			sudo systemctl reboot -i
			pause
			exit 0
		;;

		09)
			clear
			printf "Shutdown in 3s\n";
			sleep 3
			sudo systemctl poweroff -i
			pause
			exit 0
		;;


		$'\e') 
			printf "\n\nEXIT \n\n"
			exit 0
		;;

		*)
			clear
			select_function=-1
			
		;;
	esac

	show_menu_camera_selection

}



###################
#Camera functions level
###################
show_menu_camera_functions_lv1()
{

	##just kill in case it is running
	kill_darknet_slient

	back_title="Chosen Camera: ${VIDEO_CAMERA_INPUTS[$camera_num,1]} ${VIDEO_CAMERA_INPUTS[$camera_num,0]} ${VIDEO_CAMERA_INPUTS[$camera_num,5]}x${VIDEO_CAMERA_INPUTS[$camera_num,6]}@${VIDEO_CAMERA_INPUTS[$camera_num,7]}fps"

	function_selection=$(whiptail --backtitle "${back_title}" \
										--title "Camera Function" \
										--menu "Select the below functions" 25 78 14 \
										"00" "Advanced Python YoloV4 Detection Fast" \
										"01" "Advanced Python YoloV4 Detection" \
										"02" "YoloV4 Detection Selection" \
										"03" "Direct Display to HDMI" \
										"04" "Python Cam test CV2 ('F' fullscreen, esc quit)" \
										"05" "Record video to ~/xxx.mov" \
										"06" "Advanced Options" \
										"07" "Reboot" \
										"08" "Shutdown" 3>&1 1>&2 2>&3)

	case $function_selection in
		"") 
			printf "\n(Escape key)\n"
			clear
			show_menu_camera_selection
			exit 0
		;;


		00)
			clear
			echo "YoloV4 Inference"
			case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in
				"RG10")
					v4l2src_pipeline_str=${v4l2src_pipeline_str//\'/''} ##remove the ' for nvarguscamerasrc
				;;
			esac
			execute_str="python3 ~/kickstart-jetson/darknet_video_advanced.py --show_video f --video '$v4l2src_pipeline_str $v4l2src_ending_pipeline_str'"
			printf "\nDebug: $execute_str\n"
			cd ~/darknet

			echo "$execute_str" > ~/kickstart-jetson/launch.log

			eval $execute_str
		;;

		01)
			clear
			echo "YoloV4 Inference"
			case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in
				"RG10")
					v4l2src_pipeline_str=${v4l2src_pipeline_str//\'/''} ##remove the ' for nvarguscamerasrc
				;;
			esac
			execute_str="python3 ~/kickstart-jetson/darknet_video_advanced.py --show_video t --video '$v4l2src_pipeline_str $v4l2src_ending_pipeline_str'"
			printf "\nDebug: $execute_str\n"
			cd ~/darknet

			echo "$execute_str" > ~/kickstart-jetson/launch.log
			
			eval $execute_str
		;;

		02)
			clear
			echo "Yolo V4 Inference"
			show_menu_yolov3_detection_options
		;;

		03)
			clear

			execute_str="gst-launch-1.0 $v4l2src_pipeline_str nvvidconv ! 'video/x-raw(memory:NVMM), format=(string)NV12' ! nvoverlaysink sync=false async=false -e"


			printf "\nDebug v4l2src_pipeline: \n$v4l2src_pipeline_str\n"

			printf "\nDebug: $execute_str\n"
	
			eval $execute_str

			pause

		;;


		04)
			clear
			echo "Simple Python CV2 Test"
			case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in
				"RG10")
					v4l2src_pipeline_str=${v4l2src_pipeline_str//\'/''} ##remove the ' for nvarguscamerasrc
				;;
			esac
			execute_str="python3 nano_cam_test.py --video '$v4l2src_pipeline_str $v4l2src_ending_pipeline_str'"
			printf "\nDebug: $execute_str\n"
			cd ~/kickstart-jetson
			eval $execute_str
		;;

		05)
			clear
			echo "Recording Live"
			today=`date +%Y%m%d-%H%M%S`
			mkdir ~/test-videos/
			FILE="~/test-videos/LIVE-Recording-$today.mp4"


			execute_str="gst-launch-1.0 -e $v4l2src_pipeline_str nvvidconv !  tee name=t  t. ! nvv4l2h265enc bitrate=5800000 ! h265parse ! qtmux ! filesink location=$FILE -e  t. ! nvoverlaysink sync=false async=false -e "


			printf "\nDebug: $execute_str\n"
			cd ~
			eval $execute_str
		;;

		06)
			show_menu_advanced_options
		;;

		07)
			clear
			printf "Reboot in 2s\n";
			sleep 2
			sudo systemctl reboot -i
			pause

		;;

		08)
			clear
			printf "Shutdown in 3s\n";
			sleep 3
			sudo systemctl poweroff -i
			pause
		;;

		*)
		;;

	esac

	exit 0
}


###################
#Yolo v4 different detection options
###################
show_menu_yolov3_detection_options()
{
	cd ~/darknet

	if [[ -f "yolov4-tiny.weights" ]]; then
		echo "YoloV4-tiny weights exists."
	else
		cd ~/darknet
		wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights -O yolov4-tiny.weights
	fi

	back_title="Chosen Camera: ${VIDEO_CAMERA_INPUTS[$camera_num,1]} ${VIDEO_CAMERA_INPUTS[$camera_num,0]} ${VIDEO_CAMERA_INPUTS[$camera_num,5]}x${VIDEO_CAMERA_INPUTS[$camera_num,6]}@${VIDEO_CAMERA_INPUTS[$camera_num,7]}fps"

	unset dialog_menu
	dialog_menu=()

	#length of a dimension cannot be known, total array divid by 6 columns
	no_rows=${#yolo_detection_options[@]}/5
	for (( i=0; i<$no_rows; i++ ));
	do
		dialog_menu+=("${i}")
		dialog_menu+=("${yolo_detection_options[$i,0]}")
	done


	function_selection=$(whiptail --backtitle "${back_title}" \
										--title "Select Dataset for YoloV3" \
										--menu "Select Below are dataset to try out" 25 78 14 \
										"${dialog_menu[@]}" 3>&1 1>&2 2>&3)

	clear
	printf "v4l2src_pipeline_str:\n$v4l2src_pipeline_str v4l2src_ending_pipeline_str\n\n"

	if [ "$function_selection" == "" ]; then
			show_menu_camera_functions_lv1
			#printf "\n\nEXIT \n\n"
			#exit 0		
	fi
	
	echo "$function_selection ${yolo_detection_options[$function_selection,0]}  "

	case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in
		"RG10")
			#needto remove nvjpeg
			#v4l2src_pipeline_str=${v4l2src_pipeline_str//nvjpegdec/jpegdec}
			v4l2src_pipeline_str=${v4l2src_pipeline_str//\'/''} ##remove the ' for nvarguscamerasrc
		;;
	esac

	yolo_exec_str="./darknet detector demo "

	##yolo cannot use nvjpegdec
	v4l2src_pipeline_str=${v4l2src_pipeline_str//nvjpegdec/jpegdec} 

	execute_str=$(cat <<-EOF
		$yolo_exec_str \
		${yolo_detection_options[$function_selection,1]} \
		${yolo_detection_options[$function_selection,2]} \
		${yolo_detection_options[$function_selection,3]} \
		${yolo_detection_options[$function_selection,4]} \
		'$v4l2src_pipeline_str $v4l2src_ending_pipeline_str'  
	EOF
	)


	#1>&2
	#&>/dev/null &

	if (whiptail --title "Launch in interactive mode?" --yesno "Launching in debug mode or no to start background." 8 78); then
			#execute_str="nohup $execute_str &"
			echo ""
	else
			execute_str="nohup $execute_str &"
	fi

	printf "\nDebug:\n$execute_str\n\n"

	echo "$execute_str" > ~/kickstart-jetson/launch.log

	cd ~/darknet	
	eval $execute_str

	pause


}


###################
#Building the Execution String
###################
build_pipeline()
{

	#RTSPSRC
	#	rtspsrc location={} latency={} ! '
	#				'rtph264depay ! h264parse ! omxh264dec ! '
	#				'nvvidconv ! '
	#				'video/x-raw, width=(int){}, height=(int){}, '
	#				'format=(string)BGRx ! '
	#				'videoconvert ! appsink'


	v4l2src_pipeline_str="v4l2src io-mode=2 device=${VIDEO_CAMERA_INPUTS[$camera_num,0]} ! "
	#v4l2src_pipeline_str="v4l2src io-mode=2 device=${VIDEO_CAMERA_INPUTS[$camera_num,0]} do-timestamp=true ! "
	v4l2src_ending_pipeline_str=""

	case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in

		"YUYV")
			v4l2src_pipeline_str+="video/x-raw, format=YUY2, "
		;;

		"MJPG")
			v4l2src_pipeline_str+="image/jpeg, "

			#r32.2.1 Only YUV420 JPEGs 
			#v4l2src_pipeline_str+="image/jpeg, format=MJPG, "
		;;

		"H264")
			v4l2src_pipeline_str+="video/x-h264, "
		;;	

	esac


	##samson last
	v4l2src_pipeline_str+="width=${VIDEO_CAMERA_INPUTS[$camera_num,5]}, height=${VIDEO_CAMERA_INPUTS[$camera_num,6]}, framerate=$framerate/1 ! "
	##samson last
	#v4l2src_pipeline_str+=" tee name=t   t. ! "
	# t. ! v4l2sink device=/dev/video9


	case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in


		"RG10")
			#onboard camera completely different
			v4l2src_pipeline_str="nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)3264, height=(int)1848, format=(string)NV12, framerate=(fraction)15/1' ! nvvidconv flip-method=2 ! 'video/x-raw, format=(string)BGRx, width=(int)1920, height=(int)1080' ! "			

			#Zoom in
			v4l2src_pipeline_str="nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)15/1' ! nvvidconv flip-method=2 ! 'video/x-raw, format=(string)BGRx, width=(int)1280, height=(int)720' ! "					
		;;

		"YUYV")

			case $resize_to_resolution in
				"1280x720")
					v4l2src_pipeline_str+="videoscale method=bilinear sharpen=1 sharpness=2 ! video/x-raw, width=1280, height=720 ! "
				;;
				"640x360")
					v4l2src_pipeline_str+="videoscale method=bilinear sharpen=1 sharpness=2 ! video/x-raw, width=640, height=360 ! "
				;;
			esac

			if [[ $nvvidconv_flip == "flip-method=2 " ]]; then
				#v4l2src_pipeline_str+="nvvidconv flip-method=2 ! "
				v4l2src_pipeline_str+="videoflip video-direction=2 ! "
			fi			
			
		;;

		"MJPG")

			v4l2src_pipeline_str+="nvjpegdec ! video/x-raw ! "


			case $resize_to_resolution in
				"1280x720")
					v4l2src_pipeline_str+="videoscale method=1 sharpen=1 ! video/x-raw, width=1280, height=720 ! "
				;;
				"640x360")
					v4l2src_pipeline_str+="videoscale method=1 sharpen=1 ! video/x-raw, width=640, height=360 ! "
				;;
			esac

			if [[ $nvvidconv_flip == "flip-method=2 " ]]; then
				v4l2src_pipeline_str+="videoflip video-direction=2 ! "
			fi	

			##jpegdec > nvjpegdec
		
			## working with nvoverlay, not yolo
			#v4l2src_pipeline_str+="jpegparse ! nvjpegdec ! video/x-raw ! nvvidconv ! 'video/x-raw(memory:NVMM), format=(string)RGBA' ! "

			#opencv expects BGR
			
		;;

		"H264")

			v4l2src_pipeline_str+="omxh264dec enable-low-outbuffer=1 disable-dvfs=1 !"

			case $resize_to_resolution in
				"1280x720")
					v4l2src_pipeline_str+="videoscale method=1 sharpen=1 ! video/x-raw, width=1280, height=720 ! "
				;;
				"640x360")
					v4l2src_pipeline_str+="videoscale method=1 sharpen=1 ! video/x-raw, width=640, height=360 ! "
				;;
			esac

			if [[ $nvvidconv_flip == "flip-method=2 " ]]; then
				v4l2src_pipeline_str+=" videoflip video-direction=2 ! "
			fi
			
		;;	

	esac


	#if there is video_file_for_v4l2src_pipeline, then just use the video
	#useless right now, to be developed
	if [ "$video_file_for_v4l2src_pipeline" != "" ]; then

	 	#first, get the codec used, is that hevc or h264 for now
		codec_used=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$video_file_for_v4l2src_pipeline")
		case $codec_used in
			"hevc")
				v4l2src_pipeline_str="filesrc location=\"$video_file_for_v4l2src_pipeline\" ! qtdemux name=demux demux.video_0 ! queue ! h265parse ! nvv4l2decoder enable-max-performance=1 ! nvvidconv ! video/x-raw, format=BGRx ! queue ! "
			;;
			"h264")
				v4l2src_pipeline_str="filesrc location=\"$video_file_for_v4l2src_pipeline\" ! qtdemux ! queue ! h264parse ! omxh264dec ! nvvidconv ! video/x-raw, format=BGRx ! queue ! "
			;;
		esac

		case $resize_to_resolution in
			"1280x720")
				v4l2src_pipeline_str+="videoscale method=bilinear sharpen=1 sharpness=2 ! video/x-raw, width=1280, height=720 ! "
			;;
			"640x360")
				v4l2src_pipeline_str+="videoscale method=bilinear sharpen=1 sharpness=2 ! video/x-raw, width=640, height=360 ! "
			;;
		esac

		if [[ $nvvidconv_flip == "flip-method=2 " ]]; then
			v4l2src_pipeline_str+="nvvidconv flip-method=2 ! "
			#v4l2src_pipeline_str+="videoflip video-direction=2 ! "
		fi		

		printf "\nDebug: Loading File: \"$video_file_for_v4l2src_pipeline\":$codec_used\n$v4l2src_pipeline_str\n"

	fi

	case ${VIDEO_CAMERA_INPUTS[$camera_num,2]} in

		"YUYV"|"MJPG"|"H264")

			#try adding
			v4l2src_ending_pipeline_str+="nvvidconv ! video/x-raw(memory:NVMM), format=(string)I420 ! nvvidconv ! video/x-raw, format=(string)BGRx ! "
		;;

	esac

	v4l2src_ending_pipeline_str+="videoconvert ! video/x-raw, format=BGR ! "
	##v4l2src_ending_pipeline_str+="appsink sync=false async=false "

	if [ "$video_file_for_v4l2src_pipeline" != "" ]; then
		v4l2src_ending_pipeline_str+="appsink sync=false"
	else
		v4l2src_ending_pipeline_str+="appsink max-buffers=1 drop=true sync=false"
	fi

	#v4l2src_pipeline_str+=" tee name=t t. ! nvvidconv ! omxh264enc control-rate=2  bitrate=6000000 peak-bitrate=6500000  preset-level=2 profile=8 !  'video/x-h264, stream-format=(string)byte-stream, level=(string)5.2' ! h264parse ! qtmux ! filesink location=/mnt/sandisk/$today.mov t. ! "
	

	#printf "Debug:\n$v4l2src_pipeline_str\n\n";
	#pause

}


###################
#script starts here
###################




###################
#init and get environment variables
###################



shopt -s nullglob
video_camera_array=(/dev/video*)
shopt -u nullglob # Turn off nullglob to make sure it doesn't interfere with anything later

#sudo nvpmodel -q


if (( ${#video_camera_array[@]} == 0 )); then
    echo "No Cameras found" >&2


	###################
	#show some extra info here
	###################
	show_device_info

	##Todo make buzzer sound
	
    #exit 0
fi



#########----GET camera basic info


#echo "Found devices ============================";
#echo "${video_camera_array[@]}"

this_device_id="nothing"

##Getting supported camera modes
for (( i=0; i<${#video_camera_array[@]}; i++ ));
do

	this_device_id="${video_camera_array[$i]}"
	VIDEO_CAMERA_INPUTS[$i,0]="$this_device_id"

	#echo "v4l2-ctl --device=$this_device_id --list-formats-ext"
	

	#get Name
	VIDEO_CAMERA_INPUTS[$i,1]=$(v4l2-ctl --device=$this_device_id --all | grep "Card.*type" | cut -d ' ' -f 8-)

	#Rasperri pi camera
	if [[ $(v4l2-ctl --device=$this_device_id --list-formats-ext --list-formats | awk '/RG10'/ | wc -l ) > 0 ]]; 
	then
		VIDEO_CAMERA_INPUTS[$i,2]="RG10"
	fi

	if [[ $(v4l2-ctl --device=$this_device_id --list-formats-ext --list-formats | awk '/YUYV'/ | wc -l ) > 0 ]];
	then
		VIDEO_CAMERA_INPUTS[$i,2]="YUYV"
	fi

	if [[ $(v4l2-ctl --device=$this_device_id --list-formats-ext --list-formats | awk '/MJPG'/ | wc -l ) > 0 ]]; 
	then
		VIDEO_CAMERA_INPUTS[$i,2]="MJPG"
	fi

	if [[ $(v4l2-ctl --device=$this_device_id --list-formats-ext --list-formats | awk '/H264'/ | wc -l ) > 0 ]]; 
	then
		VIDEO_CAMERA_INPUTS[$i,2]="H264"
	fi

	#get Width
	#VIDEO_CAMERA_INPUTS[$i,4]=$(v4l2-ctl --device=$this_device_id --all | grep "Width\/Height" | cut -d ' ' -f 8- | cut -d '/' -f 1)

	#get Height
	#VIDEO_CAMERA_INPUTS[$i,5]=$(v4l2-ctl --device=$this_device_id --all | grep "Width\/Height" | cut -d ' ' -f 8- | cut -d '/' -f 2)


done


##----Get Frame Size
#IFS=$'\n\r'
#printf "\nGet Frame Size ============================\n\n";

for (( i=0; i<${#video_camera_array[@]}; i++ ));
do

	##empty string if it cannot detect for the tee isn't active, so cannot detect the support color space
	if [ "${VIDEO_CAMERA_INPUTS[$i,2]}" == "" ]; then
		selected_width="N/A"
		selected_height="N/A"
		continue
	fi

	#echo "$i. Doing: v4l2-ctl --device=${VIDEO_CAMERA_INPUTS[$i,0]} --list-framesizes=${VIDEO_CAMERA_INPUTS[$i,2]} "


	VIDEO_CAMERA_INPUTS[$i,3]=$( v4l2-ctl --device=${VIDEO_CAMERA_INPUTS[$i,0]} --list-framesizes=${VIDEO_CAMERA_INPUTS[$i,2]} | cut -d ' ' -f 3-  )

	#echo "${VIDEO_CAMERA_INPUTS[$i,3]}"  #in multiple line

	#put it into temp_array
	IFS=$'\n\r'
	readarray -t temp_array <<< ${VIDEO_CAMERA_INPUTS[$i,3]}

	#sort it reverse
	sorted_array=($(sort -t 'x' -k 2n <<<"${temp_array[*]}"))

	#echo "Sorted array: ${sorted_array[*]}, size: ${#temp_array[@]}"


	if [ "${#temp_array[@]}" -gt "1" ]; then
		VIDEO_CAMERA_INPUTS[$i,4]="${sorted_array[-1]}" ##THE highest resolution the cam can do
	else
		VIDEO_CAMERA_INPUTS[$i,4]="${sorted_array[0]}" ##THE highest resolution the cam can do
	fi
	

	selected_width=0
	selected_height=0


	##Manual test if 1920x1080 30fps is supported, if yes, then use if
	this_fps_string="$( v4l2-ctl --device=${VIDEO_CAMERA_INPUTS[$i,0]} --list-frameintervals=width=1920,height=1080,pixelformat=${VIDEO_CAMERA_INPUTS[$i,2]} )"

	#printf  "$this_fps_string"

	#Init assume 15fps
	framerate=15

	#detect if 60fps is supported
	if [[ $this_fps_string ==  *"60.000 fps"* ]]; then
		#printf "yes\n"
		framerate=60
		selected_width=1920
		selected_height=1080
	fi


	#if 30fps is supported, force it
	if [[ $this_fps_string ==  *"30.000 fps"* ]]; then
		#printf "yes\n"
		framerate=30
		selected_width=1920
		selected_height=1080
	fi

	##Manual test if YUYV 1920x1080 30fps is supported, if yes, then use if
	this_fps_string="$( v4l2-ctl --device=${VIDEO_CAMERA_INPUTS[$i,0]} --list-frameintervals=width=1920,height=1080,pixelformat=YUYV )"
	if [[ $this_fps_string ==  *"30.000 fps"* ]]; then
		#printf "yes\n"
		framerate=30
		selected_width=1920
		selected_height=1080
		VIDEO_CAMERA_INPUTS[$i,2]="YUYV" ##force YUYV 30fps if supported
	fi

	##skip test if 1920x1080 works

	#echo " ${#sorted_array[@]} "

	if [[ $selected_width == "0" ]]; then

		##test if it can do 30 fps by testing with string 30.000 fps
		for ((j=${#sorted_array[@]}-1; j>=0; j-- ));
		do
			this_res="${sorted_array[$j]}"
			printf  "\n[$j) $this_res]: "
			this_width=$( printf ${this_res} | cut -d 'x' -f 1 ) 
			this_height=$( printf ${this_res} | cut -d 'x' -f 2 ) 

			selected_width=$this_width
			selected_height=$this_height

			#printf  "debug: v4l2-ctl --device=${VIDEO_CAMERA_INPUTS[$i,0]} --list-frameintervals=width=$this_width,height=$this_height,pixelformat=${VIDEO_CAMERA_INPUTS[$i,2]} \n"

			this_fps_string="$( v4l2-ctl --device=${VIDEO_CAMERA_INPUTS[$i,0]} --list-frameintervals=width=$this_width,height=$this_height,pixelformat=${VIDEO_CAMERA_INPUTS[$i,2]} )"

			##printf  "$this_fps_string"

			#Init assume 15fps
			framerate=15

			#detect if 60fps is supported
			if [[ $this_fps_string ==  *"60.000 fps"* ]]; then
				framerate=60
				break
			fi


			#if 30fps is supported, force it
			if [[ $this_fps_string ==  *"30.000 fps"* ]]; then
				framerate=30
				break
			fi

		done

	fi
	

	#echo "Final array: ${sorted_array[*]}"

	VIDEO_CAMERA_INPUTS[$i,5]="${selected_width}"
	VIDEO_CAMERA_INPUTS[$i,6]="${selected_height}"
	VIDEO_CAMERA_INPUTS[$i,7]=$framerate

	#printf "\nSelected Size: ${selected_width}  x  ${selected_height}"
	#printf  "\n\n------------------------\n";

done

#########----End camera basic info


##end_num=$(( ${#video_camera_array[@]}-1 ))



function_selection=-1

if $quit_darknet; then
	function_selection="q"
fi




## autorun, then directly assume it is camera 0
if $autorun; then
	camera_num="0"

else
	#old# read -p "[0-${end_num}]: " -n1 camera_num	

	show_menu_camera_selection

fi

function_selection=""
#show_menu_advanced_options

function_selection=1



#read

## create needed dir
if [[ ! -d ~/images ]]; then
  mkdir -p ~/images;
fi

show_menu_camera_functions_lv1


display_usage_help
