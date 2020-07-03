from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
import darknet
import argparse

##can try python3 darknet_video.py --video 'v4l2src io-mode=2 device=/dev/video0 ! video/x-raw, format=YUY2, width=1920, height=1080, framerate=60/1 ! videoconvert! appsink sync=false async=false drop=true'

GST_STR = 'nvarguscamerasrc \
    ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=(fraction)30/1 \
    ! nvvidconv ! video/x-raw, width=(int)1920, height=(int)1080, format=(string)BGRx \
    ! videoconvert \
    ! appsink'



def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    return img



def myCustomActions(detections, img):
    for detection in detections:
        print ( detection[0].decode() + " : " + str(round(detection[1] * 100, 2)) + "%" )
  

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

netMain = None
metaMain = None
altNames = None

fps_time = 0

WINDOW_NAME = 'Darknet Yolo'

def main():

    full_scrn = True

    parser = argparse.ArgumentParser(description='Darknet Yolo V4 Python Detector')
    parser.add_argument("-v", "--video", required=False, default="",	help="path to input video file")
    parser.add_argument("-s", "--show_video", required=False, type=str2bool, nargs='?', const=True, default=False,	help="False for faster")
    parser.add_argument("-f", "--save_video", required=False, default="", help="Save Video output as .mp4")

    args = parser.parse_args()

 
    global metaMain, netMain, altNames
    global fps_time

    configPath = "../darknet/cfg/yolov4-tiny.cfg"
    weightPath = "../darknet/yolov4-tiny.weights"
    metaPath = "../darknet/coco.data"
    
    thresh = 0.3
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass
    #cap = cv2.VideoCapture(0)

    if ( not args.video == "" ):
        print("Loading: {}". format(args.video))
        cap = cv2.VideoCapture(args.video, cv2.CAP_GSTREAMER)
    else:
        print("Loading: {}". format(GST_STR))
        cap = cv2.VideoCapture(GST_STR, cv2.CAP_GSTREAMER)
        #cap = cv2.VideoCapture("v4l2src io-mode=2 device=/dev/video0 ! video/x-raw, format=YUY2, width=1920, height=1080, framerate=60/1 !  nvvidconv ! video/x-raw(memory:NVMM), format=(string)I420 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink sync=false async=false drop=true")

    #cap = cv2.VideoCapture("test.mp4")

    #cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_OPENGL)
    if full_scrn == True:
        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN) 
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.moveWindow(WINDOW_NAME, 0, 0)
        cv2.resizeWindow(WINDOW_NAME, 640, 360)
    else:
        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN) 
        cv2.resizeWindow(WINDOW_NAME, 640, 360)

    #cap.set(3, 1920)
    #cap.set(4, 1080)
    

    ##This will write the code
    if ( not args.save_video == "" ):
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        

        if ( args.show_video == True ):
            out_video = cv2.VideoWriter( args.save_video , fourcc, 30, (1920, 1080))
        else:
            out_video = cv2.VideoWriter( args.save_video , fourcc, 30, (darknet.network_width(netMain), darknet.network_height(netMain)))


    #out = cv2.VideoWriter(
     #   "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30.0,
     #   (darknet.network_width(netMain), darknet.network_height(netMain)))


    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect

    if ( args.show_video == True ):
        darknet_image = darknet.make_image(1920,1080,3)
    else:
        darknet_image = darknet.make_image(darknet.network_width(netMain),
                                        darknet.network_height(netMain),3)

    
                                    
    while True:

        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            # Check to see if the user has closed the window
            # If yes, terminate the program
            break      

        prev_time = time.time()
        ret, frame_read = cap.read()

        if ret != True:
            break
                    
        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)

        if ( args.show_video == True ):
            darknet.copy_image_from_bytes(darknet_image,frame_rgb.tobytes())
        else:

            frame_resized = cv2.resize(frame_rgb,
                                    (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                    interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
        
        #Printing the detections
        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=thresh)

        #print(detections)

        ### Edited the code to perform what what ever you need to
              

        if ( args.show_video == True ): 
            image = cvDrawBoxes(detections, frame_rgb)
        else:
            image = cvDrawBoxes(detections, frame_resized)
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)                 
        myCustomActions(detections,image)

        cv2.putText(image,
                    "FPS: {:.2f}" .format( (1.0 / (time.time()-prev_time)) ),
                    (10, 25),  cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        # resize image
        #dim = (640, 480)        
        #resized = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
    
        cv2.imshow(WINDOW_NAME, image)

        if ( not args.save_video == "" ):
            out_video.write(image)

        print("FPS: {:.2f}".format( 1/(time.time()-prev_time) )  )
        print("**************")


        key = cv2.waitKey(1)
        if key == 27 or key == ord("q"): # ESC 
            break

        
    cap.release()


    if ( not args.save_video == "" ):
        out_video.release()

if __name__ == "__main__":
    main()
