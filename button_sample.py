import Jetson.GPIO as GPIO
import time
from subprocess import call

shutdown_pin = 21  # Board pin 40


def button_callback(channel):

    print("Button was pushed!")    
    #sample for calling shell commands
    #call("echo MYPASSWORD | sudo -S shutdown -h now", shell=True) 
    call("uptime ", shell=True)    
    GPIO.remove_event_detect(channel)
    

def setup_button(channel):
    print("{}: RESET GPIO {} for push".format(time.time(), channel ) )
    GPIO.cleanup(channel)
    GPIO.remove_event_detect(channel)
    GPIO.setup(channel, GPIO.OUT) 
    GPIO.output(channel, GPIO.LOW)    
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    #can use GPIO.RISING / FALLING / BOTH
    GPIO.add_event_detect(channel, GPIO.RISING, callback=button_callback, bouncetime=300) # Setup event on pin 10 rising edge          


def main():
    GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)
    GPIO.remove_event_detect(shutdown_pin)

    print("Starting demo now! Press CTRL+C to exit")
  
  
    try: 

        while True:
            setup_button(shutdown_pin)
            print ('.')
            time.sleep(1)

    except KeyboardInterrupt:
        print ("Ctrl-C")
        GPIO.remove_event_detect(shutdown_pin)
    except:
        print ("Other error or exception occurred!" )
        GPIO.remove_event_detect(shutdown_pin)
    finally:
        print ("GPIO Cleanup" )
        GPIO.cleanup()




if __name__ == '__main__':
    main()