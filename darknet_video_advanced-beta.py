from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
import darknet
import argparse
from threading import Thread, enumerate
from queue import Queue
import threading

###these lines are for GPIO outputs

#for luma led display55
"""
from luma.led_matrix.device import max7219
from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, LCD_FONT
from luma.core import legacy
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
"""


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
    def __init__(self, pins, beeptimes, sleeptime): 
        threading.Thread.__init__(self)
        self.beeptimes = beeptimes
        self.sleeptime = sleeptime
        self.pins = pins


    def run(self):
        #print("starting vibrator thread")
        for i in range( len(self.pins)):
            GPIO.setup(self.pins[i], GPIO.OUT, initial=GPIO.HIGH)
        #GPIO.setup(self.pin1, GPIO.OUT, initial=GPIO.HIGH)		# added CWY 2020-08-07
        curr_value = GPIO.LOW
        for x in range(self.beeptimes):            
            for i in range( len(self.pins)):
                print("Outputting {}:{}".format(self.pins[i], curr_value) )
                GPIO.output(self.pins[i], curr_value)

            curr_value ^= GPIO.HIGH
            time.sleep(self.sleeptime)


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



#def myCustomActions(detections, img):
def myCustomActions(detections):
    global led_matrix, non_stop_buzzer


    for detection in detections:
        print ( detection[0].decode() + " : " + str(round(detection[1] * 100, 2)) + "%" )
#        if detection[0].decode() == "person" :
#            led_matrix("a")
#            #oled works, but causes slowdown
#            oled(detection[0].decode())
#
#        if detection[0].decode() == "car" :
#            led_matrix("d")
#            #oled works, but causes slowdown
#            #oled(detection[0].decode())


        if detection[0].decode() == "cell phone" :
            print ("I am Cell Phone")
            #if not buzzer_f.isAlive():
                #buzzer_f.start()

        """
        if detection[0].decode() == "GOFORWARD" :
            if not buzzer_f.isAlive():
                buzzer_f.start()

        if detection[0].decode() == "GOLEFT" :
            if not buzzer_l.isAlive():
                buzzer_l.start()

        if detection[0].decode() == "GORIGHT" :
            if not buzzer_r.isAlive():
                buzzer_r.start()

        if detection[0].decode() == "SLOWFORWARD" :
            if not buzzer_s.isAlive():
                buzzer_s.start()            

        if detection[0].decode() == "STOP" :
            if not buzzer_t.isAlive():
                buzzer_t.start()      
        """
    

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


fps_time = 0

WINDOW_NAME = 'Darknet Yolo'
video_width = 1920
video_height = 1080

def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    """
    parser.add_argument("--input", type=str, default=0,
                        help="video source. If empty, uses webcam 0 stream")
    """
    parser.add_argument("--out_filename", type=str, default="",
                        help="inference video name. Not saved if empty")
    parser.add_argument("--weights", default="yolov4.weights",
                        help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true',
                        help="windown inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true',
                        help="display bbox coordinates of detected objects")
    parser.add_argument("--config_file", default="./cfg/yolov4.cfg",
                        help="path to config file")
    parser.add_argument("--data_file", default="./cfg/coco.data",
                        help="path to data file")
    parser.add_argument("--thresh", type=float, default=.25,
                        help="remove detections with confidence below this value")

    parser.add_argument("-v", "--video", required=True, default="",	help="path to input video file, If empty, uses webcam 0 stream")
    parser.add_argument("-s", "--show_video", required=False, type=str2bool, nargs='?', const=True, default=False,	help="False for faster")
    #parser.add_argument("-f", "--save_video", required=False, default="", help="Save Video output as .mp4")

    return parser.parse_args()

def str2int(video_path):
    """
    argparse returns and string althout webcam uses int (0, 1 ...)
    Cast to int if needed
    """
    try:
        return int(video_path)
    except ValueError:
        return video_path


def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    """
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    
    if str2int(args.video) == str and not os.path.exists(args.video):
        raise(ValueError("Invalid video path {}".format(os.path.abspath(args.video))))
    """


def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    video = cv2.VideoWriter(output_video, fourcc, fps, size)
    return video


def video_capture(frame_queue, darknet_image_queue):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("video_capture failed")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        frame_queue.put(frame_resized)
        darknet.copy_image_from_bytes(darknet_image, frame_resized.tobytes())
        darknet_image_queue.put(darknet_image)
    cap.release()

def inference(darknet_image_queue, detections_queue, fps_queue):
    while cap.isOpened():
        darknet_image = darknet_image_queue.get()
        prev_time = time.time()
        detections = darknet.detect_image(network, class_names, darknet_image, thresh=args.thresh)
        detections_queue.put(detections)
        fps = int(1/(time.time() - prev_time))
        fps_queue.put(fps)
        print("FPS: {}".format(fps))
        darknet.print_detections(detections, args.ext_output)
    cap.release()

def drawing(frame_queue, detections_queue, fps_queue):
    random.seed(3)  # deterministic bbox colors
    video = set_saved_video(cap, args.out_filename, (width, height))
    while cap.isOpened():
        frame_resized = frame_queue.get()
        detections = detections_queue.get()
        fps = fps_queue.get()
        if frame_resized is not None:
            image = darknet.draw_boxes(detections, frame_resized, class_colors)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if args.out_filename is not None:
                video.write(image)
            if not args.dont_show:
                cv2.imshow('Inference', image)
            if cv2.waitKey(fps) == 27:
                break

    cap.release()
    video.release()
    cv2.destroyAllWindows()    

if __name__ == '__main__':

    full_scrn = True

    frame_queue = Queue()
    darknet_image_queue = Queue(maxsize=1)
    detections_queue = Queue(maxsize=1)
    fps_queue = Queue(maxsize=1)

    args = parser()
    check_arguments_errors(args)

    configPath = "../trained-weights/reference/yolov4-tiny.cfg"
    weightPath = "../trained-weights/reference/yolov4-tiny.weights"
    metaPath = "../trained-weights/reference/coco.data"
    #configPath = "../track/yolov4-tiny.cfg"
    #weightPath = "../track/yolov4-tiny_final.weights"
    #metaPath = "../track/obj-google.data"

    '''
    network, class_names, class_colors = darknet.load_network(
            args.config_file,
            args.data_file,
            args.weights,
            batch_size=1
        )
    '''

    network, class_names, class_colors = darknet.load_network(
        configPath,
        metaPath,
        weightPath,
        batch_size=1
    ) 



    
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)  
    #width = video_width  
    height = darknet.network_height(network)
    #height = video_height
    darknet_image = darknet.make_image(width, height, 3)
    #input_path = str2int(args.video)
    input_path = args.video
    print("*************")
    print(width)
    print(height)
    print("*************")
    input_path = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! appsink sync=false drop=true max-buffers=1'
    
    input_path = "/home/jetsonnano/test-videos/_Mask-global-shutter-Kowloon-West-Promenade0.mp4"

    cap = cv2.VideoCapture(input_path)

    if cap.isOpened():
        print("Starting the YOLO loop...")
    else:
        print("main failed")


    Thread(target=video_capture, args=(frame_queue, darknet_image_queue)).start()
    Thread(target=inference, args=(darknet_image_queue, detections_queue, fps_queue)).start()
    Thread(target=drawing, args=(frame_queue, detections_queue, fps_queue)).start()

    #cap = cv2.VideoCapture("test.mp4")


#    #cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_OPENGL)
#    if full_scrn == True:
#        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN) 
#        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#        cv2.moveWindow(WINDOW_NAME, 0, 0)
#        cv2.resizeWindow(WINDOW_NAME, 640, 360)
#    else:
#        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN) 
#        cv2.resizeWindow(WINDOW_NAME, 640, 360)

    #cap.set(3, video_width)
    #cap.set(4, video_height)
    
    #out = cv2.VideoWriter(
     #   "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30.0,
     #   (darknet.network_width(netMain), darknet.network_height(netMain)))


    

    """
    buzzer_f = VibratorThread( [17], 3, 0.5)
    buzzer_l = VibratorThread( [18], 3, 0.5)
    buzzer_r = VibratorThread( [27], 3, 0.5)
    buzzer_s = VibratorThread( [24], 3, 0.5)
    buzzer_t = VibratorThread( [17,18,27,24], 3, 0.5)    
    """

    # Create an image we reuse for each detect

#    if ( args.show_video == True ):
#        darknet_image = darknet.make_image(video_width,video_height,3)
#    else:
#        darknet_image = darknet.make_image(darknet.network_width(netMain),
#                                        darknet.network_height(netMain),3)

    #faulthandler.enable()
                                    
#    while True:
#
#
#
#
#        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
#            # Check to see if the user has closed the window
#            # If yes, terminate the program
#
#            
#            #stop the buzzer
#            if non_stop_buzzer.isAlive():
#                try:
#                    non_stop_buzzer.stopit()
#                    non_stop_buzzer.join()
#                except:
#                    pass        
#            break            
#            
                 
#        

#        prev_time = time.time()
#        ret, frame_read = cap.read()

#        
#        if ret != True:
#            print("Video open failed, run:")
#            print("sudo systemctl restart nvargus-daemon")
#            break
#        

#        cv2.imshow(WINDOW_NAME, frame_read)                 
#        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)

#        if ( args.show_video == True ):
#            darknet.copy_image_from_bytes(darknet_image,frame_rgb.tobytes())
#        else:

#            frame_resized = cv2.resize(frame_rgb,
#                                    (darknet.network_width(netMain),
#                                    darknet.network_height(netMain)),
#                                    interpolation=cv2.INTER_LINEAR)

#            

#            darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
#        
#        #Printing the detections
#        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=thresh)

#        #print(detections)

#        ### Edited the code to perform what what ever you need to
#              

#        if ( args.show_video == True ):             
#            image = cvDrawBoxes(detections, frame_rgb)
#        else:
#            
#            image = cvDrawBoxes(detections, frame_resized)
#        
#        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#        #myCustomActions(detections,image)
#        myCustomActions(detections)

#        cv2.putText(image,
#                    "FPS: {:.2f}" .format( (1.0 / (time.time()-prev_time)) ),
#                    (10, 25),  cv2.FONT_HERSHEY_SIMPLEX, 1,
#                    (0, 255, 0), 2)

#        # resize image
#        #dim = (640, 480)        
#        #resized = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
#    
#        cv2.imshow(WINDOW_NAME, image)

#        if ( not args.save_video == "" ):
#            out_video.write(image)

#        print("FPS: {:.2f}".format( 1/(time.time()-prev_time) )  )
#        print("**************")
#

#        key = cv2.waitKey(1)
#        if key == 27 or key == ord("q"): # ESC 
#            #stop the buzzer
#            """
#            if non_stop_buzzer.isAlive():
#                try:
#                    non_stop_buzzer.stopit()
#                    non_stop_buzzer.join()
#                except:
#                    pass        
#            break
#            """

        
    cap.release()
    GPIO.cleanup()


