import cv2
import argparse
import time

GST_STR = 'nvarguscamerasrc \
    ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=(fraction)30/1 \
    ! nvvidconv ! video/x-raw, width=(int)1920, height=(int)1080, format=(string)BGRx \
    ! videoconvert \
    ! appsink'
WINDOW_NAME = 'Camera Test'

fps_time = 0


def main():
    parser = argparse.ArgumentParser(description='Cam test')

    parser.add_argument("-v", "--video", required=True,	help="path to input video file")

    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video, cv2.CAP_GSTREAMER)
    
    #*cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_OPENGL)
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN) 
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(WINDOW_NAME, 0, 0)
    cv2.resizeWindow(WINDOW_NAME, 640, 360)
    
    

    #skip writing
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')    
    #out_video = cv2.VideoWriter('output.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (1920, 1080))
    #out_video = cv2.VideoWriter('output.mp4', fourcc, 30, (1920, 1080))
    
    full_scrn = True
    fps = 0.0
    tic = time.time()

    global fps_time

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            # Check to see if the user has closed the window
            # If yes, terminate the program
            break                        
            
        ret, image = cap.read()

        if ret != True:
            break


        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 25),  cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)
        
        cv2.imshow(WINDOW_NAME, image)


        #out_video.write(image)

        fps_time = time.time()
        key = cv2.waitKey(1)

        if key == 27 or key == ord("q"): # ESC 
            break
        elif key == ord('F') or key == ord('f'):  # Toggle fullscreen

            if full_scrn:
                 cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            else:
                 cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            full_scrn = not full_scrn

    cap.release()
    cv2.destroyAllWindows()
    #out_video.release()
    #logger.debug('finished+')
if __name__ == "__main__":
    main()