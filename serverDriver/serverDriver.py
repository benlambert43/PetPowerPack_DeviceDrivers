import serial
import platform

CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''

if (CURRENT_PLATFORM == 'Linux'):
    SERIAL_PORT = '/dev/ttyUSB0'
elif (CURRENT_PLATFORM == 'Windows'):
    SERIAL_PORT = 'COM3'


f = open('SRoutput.txt', 'wb')



arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=100)


i = 0
try:
    while True:
        print("Receiving data packet " + str(i))
        f.write(arduino.readline())
        i = i+1

except KeyboardInterrupt:
    print("Saving and closing...")
    f.close()
    exit()