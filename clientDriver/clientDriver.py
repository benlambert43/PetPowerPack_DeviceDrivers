# Importing Libraries
import serial

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=100)
def write(x):
    arduino.write(bytes(x+'\n', 'utf-8'))

injection = input("Send code to Arduino Client: ") # Taking input from user
value = write(injection)
