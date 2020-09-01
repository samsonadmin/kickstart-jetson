import Jetson.GPIO as GPIO
import time



shutdown_pin = 21  # Board pin 18

def button_callback(channel):
    print("Button was pushed, shutdown now!")
    from subprocess import call
    call("echo asdfQWER | sudo -S shutdown -h now", shell=True)    

    
def main():
    # Pin Setup:
    #GPIO.cleanup()


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

    
    time.sleep(10)
    GPIO.remove_event_detect(shutdown_pin)


if __name__ == '__main__':
    main()