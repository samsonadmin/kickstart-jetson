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


import threading
#for luma led display55
"""
import serial
from luma.led_matrix.device import max7219
from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, LCD_FONT
from luma.core import legacy
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
"""

#for buzzer
import Jetson.GPIO as GPIO


shutdown_pin = 21  # Board pin 18

def button_callback(channel):
    print("Button was pushed, shutdown now!")
    from subprocess import call
    call("echo asdfQWER | sudo -S shutdown -h now", shell=True)    



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
    hello_arrow_bitmap_font=[ [0xbd,0x42,0xa5,0x99,0x99,0xa5,0x42,0xbd] ]
    dont_arrow_bitmap_font=[[0x18,0x24,0x04,0x08,0x10,0x10,0x00,0x10]]
                      
    if led_matrix_ok:
        with canvas(led_device) as draw:        
            if display_text == "w":
                legacy.text(draw, (0, 0), "\0", fill="white", font=up_arrow_bitmap_font)
            elif display_text == "a":
                legacy.text(draw, (0, 0), "\0", fill="white", font=dont_arrow_bitmap_font)
                #legacy.text(draw, (0, 0), "\0", fill="white", font=left_turn_arrow_bitmap_font)
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

"""
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

"""

GPIO.setmode(GPIO.BCM)

class VibratorThread(threading.Thread):
    def __init__(self, pins, beeptimes, sleeptime, *args, **kwargs): 
        super(VibratorThread, self).__init__(*args, **kwargs) 
        self._stopper = threading.Event() 
        self.beeptimes = beeptimes
        self.sleeptime = sleeptime
        self.pins = pins
        self.run_again = False
        for i in range( len(self.pins)):
            GPIO.setup(self.pins[i], GPIO.OUT, initial=GPIO.HIGH)        
            #print("Outputting {}:{}".format(self.pins[i], curr_value) )
            GPIO.output(self.pins[i], False)

     #  (avoid confusion)
    def stopit(self):       
        self._stopper.set() # ! must not use _stop
        GPIO.output(output_pin, GPIO.LOW)       
  
    def stopped(self): 
        return self._stopper.isSet() 


    def run(self):
        #print("starting vibrator thread")
        while True:

            if self.stopped(): 
                return

            if self.run_again:      
                print("restarting vibrator thread")
                #GPIO.setup(self.pin1, GPIO.OUT, initial=GPIO.HIGH)		# added CWY 2020-08-07
                curr_value = True
                for x in range(self.beeptimes):            
                    for i in range( len(self.pins)):
                        print("Outputting {}:{}".format(self.pins[i], curr_value) )
                        GPIO.output(self.pins[i], curr_value)

                    if curr_value:
                        curr_value = False
                    else:
                        curr_value = True

                    time.sleep(self.sleeptime)
                self.run_again = False
            else:
                time.sleep(0.5)





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
        # set pin as an output pin with optional initial state of LOW
        GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
        curr_value = GPIO.HIGH        

        while True:
            if self.stopped(): 
                return

            print("Outputting {} to pin {}".format(curr_value, output_pin))
            GPIO.output(output_pin, curr_value)
            curr_value ^= GPIO.HIGH                     
            time.sleep(0.5) 




"""
non_stop_buzzer = NonStopBuzzerThread()
"""


###these lines are for GPIO outputs ends


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


tester = 1

def myCustomActions(detections, img):
    global led_matrix, buzzer_f, buzzer_l, buzzer_r, buzzer_s, buzzer_t
    global tester

    for detection in detections:
        print ( detection[0].decode() + " : " + str(round(detection[1] * 100, 2)) + "%" )


        if detection[0].decode() == "GOFORWARD" :
            buzzer_f.run_again = True

        if detection[0].decode() == "GOLEFT" :
            buzzer_l.run_again = True

        if detection[0].decode() == "GORIGHT" :
            buzzer_r.run_again = True

        if detection[0].decode() == "SLOWFORWARD" :
            buzzer_s.run_again = True  

        if detection[0].decode() == "STOP" :
            buzzer_f.run_again = True 
     

"""
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
"""


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
video_width = 1920
video_height = 1080


#this is need to stop the running threads, otherwise buzzer continues to make sounds
import signal, sys
def graceful_exit(sig, frame):
    print('You pressed Ctrl+C/Z!')

    try:
        buzzer_f.stopit()
        buzzer_f.join()
        buzzer_l.stopit()
        buzzer_l.join()
        buzzer_r.stopit()
        buzzer_r.join()
        buzzer_s.stopit()
        buzzer_s.join()
        buzzer_t.stopit()
        buzzer_t.join()
    except:
        pass        

    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTSTP, graceful_exit)
#################


def main():

    full_scrn = True

    parser = argparse.ArgumentParser(description='Darknet Yolo V4 Python Detector')
    parser.add_argument("-v", "--video", required=False, default="",	help="path to input video file")
    parser.add_argument("-s", "--show_video", required=False, type=str2bool, nargs='?', const=True, default=False,	help="False for faster")
    parser.add_argument("-f", "--save_video", required=False, default="", help="Save Video output as .mp4")

    args = parser.parse_args()

 
    global led_matrix, buzzer_f, buzzer_l, buzzer_r, buzzer_s, buzzer_t
    global metaMain, netMain, altNames
    global fps_time

    configPath = "../darknet/cfg/yolov4-csp.cfg"
    weightPath = "../darknet/yolov4-csp.weights"
    metaPath = "coco.data"
    #configPath = "../track/yolov4-tiny.cfg"
    #weightPath = "../track/yolov4-tiny_final.weights"
    #metaPath = "../track/obj-google.data"
    
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

    #cap.set(3, video_width)
    #cap.set(4, video_height)
    

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

    
    buzzer_f = VibratorThread( [27], 2, 0.5)
    buzzer_l = VibratorThread( [17], 2, 0.3)
    buzzer_r = VibratorThread( [18], 2, 0.3)
    buzzer_s = VibratorThread( [27], 2, 1)
    buzzer_t = VibratorThread( [17,18], 2, 2)    
    
    buzzer_f.start()
    buzzer_l.start()
    buzzer_r.start()
    buzzer_s.start()
    buzzer_t.start()



    # Create an image we reuse for each detect

    if ( args.show_video == True ):
        darknet_image = darknet.make_image(video_width,video_height,3)
    else:
        darknet_image = darknet.make_image(darknet.network_width(netMain),
                                        darknet.network_height(netMain),3)

    #faulthandler.enable()



    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.remove_event_detect(shutdown_pin)

    print("Starting demo now! Press CTRL+C to exit")

    
    try: 
        print("Setting Shutdown to LOW")
        GPIO.setup(shutdown_pin, GPIO.OUT) 
        GPIO.output(shutdown_pin, GPIO.LOW)
        ##time.sleep(1)
        GPIO.cleanup(shutdown_pin)
        GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        GPIO.add_event_detect(shutdown_pin, GPIO.BOTH, callback=button_callback) # Setup event on pin 10 rising edge          

    finally:
        pass




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
            
                 
        

        prev_time = time.time()
        ret, frame_read = cap.read()

        
        if ret != True:
            print("Video open failed, run:")
            print("sudo systemctl restart nvargus-daemon")
            break
        

        cv2.imshow(WINDOW_NAME, frame_read)                 
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
        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=thresh, debug=False)

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

            try:
                buzzer_f.stopit()
                buzzer_f.join()
                buzzer_l.stopit()
                buzzer_l.join()
                buzzer_r.stopit()
                buzzer_r.join()
                buzzer_s.stopit()
                buzzer_s.join()
                buzzer_t.stopit()
                buzzer_t.join()
            except:
                pass

            #stop the buzzer
            """
            if non_stop_buzzer.isAlive():
                try:
                    non_stop_buzzer.stopit()
                    non_stop_buzzer.join()
                except:
                    pass        
            break
            """

        
    cap.release()
    GPIO.cleanup()


    if ( not args.save_video == "" ):
        out_video.release()

if __name__ == "__main__":
    main()
