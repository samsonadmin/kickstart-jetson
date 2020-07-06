from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
import darknet
import argparse


###these lines are for GPIO outputs

import serial
import threading
#for luma led display
from luma.led_matrix.device import max7219
from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, LCD_FONT
from luma.core import legacy
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

#for buzzer
import Jetson.GPIO as GPIO


def led_matrix(display_text):
    global led_matrix_ok

    #https://www.riyas.org/2013/12/online-led-matrix-font-generator-with.html
    up_arrow_bitmap_font = [ [0x18,0x3c,0x7e,0xdb,0x99,0x99,0x18,0x18] ]
    left_arrow_bitmap_font = [ [0x38,0x0c,0x06,0xff,0xff,0x06,0x0c,0x38] ]
    left_turn_arrow_bitmap_font = [ [0x30,0x60,0xfc,0xfe,0x63,0x33,0x06,0x0c] ]
    right_turn_arrow_bitmap_font = [ [0x0c,0x06,0x3f,0x7f,0xc6,0x6c,0x30,0x18] ]
    right_arrow_bitmap_font = [ [0x18,0x0c,0x06,0xff,0xff,0x06,0x0c,0x18] ]
    down_arrow_bitmap_font = [ [0x18,0x18,0x99,0x99,0xdb,0x7e,0x3c,0x18] ]
    stop_arrow_bitmap_font = [ [0x3c,0x42,0x40,0x3c,0x02,0x42,0x42,0x3c] ]

    if led_matrix_ok:
        with canvas(led_device) as draw:        
            if display_text == "w":
                legacy.text(draw, (0, 0), "\0", fill="white", font=up_arrow_bitmap_font)
            elif display_text == "a":
                legacy.text(draw, (0, 0), "\0", fill="white", font=left_turn_arrow_bitmap_font)
            elif display_text == "d":
                legacy.text(draw, (0, 0), "\0", fill="white", font=right_turn_arrow_bitmap_font)
            elif display_text == "s":
                legacy.text(draw, (0, 0), "\0", fill="white", font=stop_arrow_bitmap_font)
            else:
                text(draw, (1, 1), display_text, fill="white", font=proportional(LCD_FONT))

def oled(display_text):
    global oled_ok, oled_font, oled_device
    if oled_ok:
        with canvas(oled_device) as draw:
            draw.text( (0, 0), display_text, fill="white", font=oled_font)        

try:
    #https://ssd1306.readthedocs.io/en/latest/python-usage.html
    serial_i2c = i2c(port=1, address=0x3c)
    oled_device = ssd1306(serial_i2c)
    oled_font = ImageFont.truetype("/home/jetsonnano/kickstart-jetson/BenchNine-Regular.ttf", 35)
    print("Created OLED device")
    oled_ok = True
except:
    oled_ok = False

try:
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    led_device = max7219(serial, width=8, height=8, rotate=1, block_orientation=0)
    print("Created MATRIX device")
    oled("Loaded...")
    led_matrix_ok = True

except:
    led_matrix_ok = False



# Pin Definitions
output_pin = 12  # BOARD pin 12, BCM pin 18

last_serial_command_sent = ""
next_serial_command_to_send = ""
fall_detected_outer_rectangle_is_on = False
halt_non_stop_buzzer_thread = False

def buzzer_thread(beeptimes, sleeptime):

    GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    curr_value = GPIO.HIGH

    try:
        for x in range(beeptimes):            
            # Toggle the output every second
            print("Outputting {} to pin {}".format(curr_value, output_pin))
            GPIO.output(output_pin, curr_value)
            curr_value ^= GPIO.HIGH
            time.sleep(sleeptime)
    finally:
        GPIO.cleanup()
        buzzer = threading.Thread(target=buzzer_thread, args=(2,0.02, ))


class NonStopBuzzerThread(threading.Thread):
    #https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/

    def __init__(self, *args, **kwargs): 
        super(NonStopBuzzerThread, self).__init__(*args, **kwargs) 
        self._stopper = threading.Event() 
  
     #  (avoid confusion)
    def stopit(self):       
        self._stopper.set() # ! must not use _stop
        GPIO.output(output_pin, GPIO.LOW)       
  
    def stopped(self): 
        return self._stopper.isSet() 
  
    def run(self): 
        GPIO.setmode(GPIO.BCM)
        #GPIO.setmode(GPIO.BOARD)
        # set pin as an output pin with optional initial state of HIGH
        GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
        curr_value = GPIO.HIGH        

        while True:
            if self.stopped(): 
                return

            print("Outputting {} to pin {}".format(curr_value, output_pin))
            GPIO.output(output_pin, curr_value)
            curr_value ^= GPIO.HIGH                     
            time.sleep(0.5) 


non_stop_buzzer = NonStopBuzzerThread()

buzzer = threading.Thread(target=buzzer_thread, args=(2,0.04, ))


###these lines are for GPIO outputs ends


##can try python3 darknet_video.py --video 'v4l2src io-mode=2 device=/dev/video0 ! video/x-raw, format=YUY2, width=1920, height=1080, framerate=60/1 ! videoconvert! appsink sync=false async=false drop=true'


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
    global led_matrix, non_stop_buzzer

    for detection in detections:
        print ( detection[0].decode() + " : " + str(round(detection[1] * 100, 2)) + "%" )
        if detection[0].decode() == "person" :
            led_matrix("a")
            #oled works, but causes slowdown
            #oled(detection[0].decode())

        if detection[0].decode() == "car" :
            led_matrix("d")
            #oled works, but causes slowdown
            #oled(detection[0].decode())


    #If detected something
    if len(detections) > 0:

        #make the buzzer sound
        if not non_stop_buzzer.isAlive():                
            non_stop_buzzer.start()

        #make LED Light on P26, please use NPN transistor, don't connect directly
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT, initial=GPIO.HIGH)

    else:
        #stop the buzzer
        if non_stop_buzzer.isAlive():
            try:
                non_stop_buzzer.stopit()
                non_stop_buzzer.join()
                non_stop_buzzer = NonStopBuzzerThread() ##create a new thread
            except:
                pass

        #make LED Light on P26 LOW, , please use NPN transistor, don't connect directly
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT, initial=GPIO.LOW)

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
video_width = 1280
video_height = 720

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
            out_video = cv2.VideoWriter( args.save_video , fourcc, 30, (video_width, video_height))
        else:
            out_video = cv2.VideoWriter( args.save_video , fourcc, 30, (darknet.network_width(netMain), darknet.network_height(netMain)))


    #out = cv2.VideoWriter(
     #   "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30.0,
     #   (darknet.network_width(netMain), darknet.network_height(netMain)))


    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect

    if ( args.show_video == True ):   
        darknet_image = darknet.make_image(video_width,video_height,3)
    else:
        darknet_image = darknet.make_image(darknet.network_width(netMain),
                                        darknet.network_height(netMain),3)

    


                                    
    while True:

        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            # Check to see if the user has closed the window
            # If yes, terminate the program

            #stop the buzzer
            if non_stop_buzzer.isAlive():
                try:
                    non_stop_buzzer.stopit()
                    non_stop_buzzer.join()
                except:
                    pass        
            break            
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
            #stop the buzzer
            if non_stop_buzzer.isAlive():
                try:
                    non_stop_buzzer.stopit()
                    non_stop_buzzer.join()
                except:
                    pass        
            break

        
    cap.release()


    if ( not args.save_video == "" ):
        out_video.release()

if __name__ == "__main__":
    main()
