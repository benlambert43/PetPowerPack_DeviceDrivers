import serial
import platform
import dbEnvConnectors
import mysql.connector


CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''

if (CURRENT_PLATFORM == 'Linux'):
    SERIAL_PORT = '/dev/ttyUSB0'
elif (CURRENT_PLATFORM == 'Windows'):
    SERIAL_PORT = 'COM3'


f = open('SRoutput.txt', 'wb')



arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=100)

print("connecting to db on " + dbEnvConnectors.getDB().host)
mydb = mysql.connector.connect(
  host=dbEnvConnectors.getDB().host,
  user=dbEnvConnectors.getDB().user,
  password=dbEnvConnectors.getDB().password
)

print(mydb)
mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)

i = 0
try:
    while True:
        lineFromHC12 = arduino.readline()
        print("Receiving data packet " + str(i))
        f.write(lineFromHC12)

        if (lineFromHC12.decode("utf-8").startswith("PointNumber")):
            print(lineFromHC12)

        i = i+1

except KeyboardInterrupt:
    print("Saving and closing...")
    f.close()
    exit()