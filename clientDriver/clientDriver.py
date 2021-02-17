import serial
import platform

CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''

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


injection = input("Send code to Arduino Client: ")
value = write(injection)
while(True):
    readGPS = str(readFromSerial())
    print(readGPS)
