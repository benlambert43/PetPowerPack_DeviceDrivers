# Importing Libraries
import serial

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=100)
def write(x):
    arduino.write(bytes(x+'\n', 'utf-8'))
def readFromSerial():
    line = arduino.readline()
    return line


injection = input("Send code to Arduino Client: ")
value = write(injection)
while(True):
    readGPS = readFromSerial()
    print(readGPS)
