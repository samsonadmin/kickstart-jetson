#!/usr/bin/python3
import time
import serial

print("UART Demonstration Program")
print("NVIDIA Jetson Nano Developer Kit")


serial_port = serial.Serial(
    port="/dev/ttyUSB0",
    #port="/dev/ttyTHS1",
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
# Wait a second to let the port initialize
time.sleep(1)

try:
    # Send a simple header
#    serial_port.write("q\r\n".encode())
#    serial_port.write("e\r\n".encode())
#    serial_port.write("w\r\n".encode())
#    serial_port.write("a\r\n".encode())
#    serial_port.write("s\r\n".encode())
#    serial_port.write("d\r\n".encode())
    while True:
        serial_port.write("q\r\n".encode())
        serial_port.write("w\r\n".encode())
        
        serial_port.write("e\r\n".encode())
        #serial_port.write("\r\n".encode())
        serial_port.write("s\r\n".encode())
        #serial_port.write("\r\n".encode())
        


            
        if serial_port.inWaiting() > 0:
         
            data = serial_port.read()
            print(data)
            #serial_port.write(data)
            # if we get a carriage return, add a line feed too
            # \r is a carriage return; \n is a line feed
            # This is to help the tty program on the other end 
            # Windows is \r\n for carriage return, line feed
            # Macintosh and Linux use \n
            #if data == "\r".encode():
                # For Windows boxen on the other end
            #    serial_port.write("\n".encode())
    
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting Program")

except Exception as exception_error:
    print("Error occurred. Exiting Program")
    print("Error: " + str(exception_error))

finally:
    serial_port.close()
    pass
