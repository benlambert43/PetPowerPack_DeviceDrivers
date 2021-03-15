import serial
import platform
import cv2
import base64
import time

CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''
vid = cv2.VideoCapture(0) 
f = open('CLoutput.txt', 'wb')



if (CURRENT_PLATFORM == 'Linux'):
    SERIAL_PORT = '/dev/ttyUSB0'
elif (CURRENT_PLATFORM == 'Windows'):
    SERIAL_PORT = 'COM4'


arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=100)

def write(x):
    try:
        arduino.write(bytes(x+'\n', 'utf-8'))
        return True
    except:
        return False

def readFromSerial():
    line = arduino.readline()
    return line


# injection = input("Send code to Arduino Client: ")
# value = write(injection)
i = 0;
while(True):
    # Capture the video frame 
    # by frame 
    ret, frame = vid.read() 
  
    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)


    #f.write(jpg_as_text)

    gpsCoords = readFromSerial();
    write("PointNumber: " + str(i) + " GPS: " + str(gpsCoords) + " IMG: ")
    

    i = i+1
    time.sleep(3)
    

vid.release() 
cv2.destroyAllWindows() 
f.close()