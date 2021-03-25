import serial
import platform
import cv2
import time
import online
import offline
import threading
import http.client as httplib


CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''
camera = cv2.VideoCapture(0)



if (CURRENT_PLATFORM == 'Linux'):
    SERIAL_PORT = '/dev/ttyACM0'
elif (CURRENT_PLATFORM == 'Windows'):
    SERIAL_PORT = 'COM4'

arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=200)


def detectInternet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False


def write(x):
    try:
        time.sleep(1)
        arduino.write(bytes(x+'\n', 'utf-8'))
        time.sleep(1)
        return True
    except:
        time.sleep(1)
        return False

def readFromSerial():
    time.sleep(1)
    line = arduino.readline()
    time.sleep(1)
    return line



if __name__ == "__main__":
    # creating thread
    t1 = threading.Thread(target=offline.offlineThread, args=(write, readFromSerial, camera, detectInternet,))
    t1.daemon = True
    t1.start()

    online.onlineVideoFeed(camera)

    # keep daemon threads alive
    while True:
        time.sleep(1)





