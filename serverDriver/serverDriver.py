import serial
import platform
import dbEnvConnectors
import mysql.connector

# Environment Variables
CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''

# Detect which serial file reader to use
if (CURRENT_PLATFORM == 'Linux'):
    SERIAL_PORT = '/dev/ttyUSB0'
elif (CURRENT_PLATFORM == 'Windows'):
    SERIAL_PORT = 'COM3'

# Write to temp file for debugging
f = open('SRoutput.txt', 'w')

# Connect to Arduino over serial port
arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=100)

# Connect to the local MySQL DB
print("checking for database on " + dbEnvConnectors.getDB().host)
mydbconnection1 = mysql.connector.connect(
  host=dbEnvConnectors.getDB().host,
  user=dbEnvConnectors.getDB().user,
  password=dbEnvConnectors.getDB().password
)

# Initialize the cursor opject on the database
mycursor = mydbconnection1.cursor()


# Find out if the petpowerpackserverdb already exists on the server.
# If it doesn't, create it.
mycursor.execute("SHOW DATABASES")
dbArray = []
for x in mycursor:
  dbArray.append(str(x))

alreadyContainsDB = False;
for dbstr in dbArray:
    normalizeStr = str(dbstr)
    if (normalizeStr.__contains__("petpowerpackserverdb")):
        alreadyContainsDB = True;

if (not(alreadyContainsDB)):
    print("Creating PetPowerPackServerDB...")
    create_db_query = "CREATE DATABASE PetPowerPackServerDB"
    mycursor.execute(create_db_query)
else:
    print("PetPowerPackServerDB already exists. Skipping creation and connecting instead.")
mydbconnection1.commit()
mydbconnection1.close()


print("connecting to db on " + dbEnvConnectors.getDB().host)
mydb = mysql.connector.connect(
  host=dbEnvConnectors.getDB().host,
  user=dbEnvConnectors.getDB().user,
  password=dbEnvConnectors.getDB().password,
  database="petpowerpackserverdb"
)

mysqlCmdCursor = mydb.cursor()
createTableCommand = 'CREATE TABLE IF NOT EXISTS `image` ( `imageID` bigint unsigned NOT NULL AUTO_INCREMENT, `imageNumber` bigint unsigned NOT NULL, `imagePacketNumber` bigint unsigned NOT NULL, `packetData` varchar(2048) DEFAULT NULL, `pointAssoc` bigint unsigned NOT NULL, PRIMARY KEY (`imageID`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
mysqlCmdCursor.execute(createTableCommand)
mydb.commit()


i = 0
try:
    while True:
        lineFromHC12 = arduino.readline()
        print("Receiving data packet " + str(i))
        if (lineFromHC12.decode("utf-8").startswith("imageNumber")):
            packetDataStr = lineFromHC12.decode("utf-8")
            onlyImageStartIndex = packetDataStr.rfind("packetData:") + (len("packetData: "))
            onlyImageEndIndex = len(packetDataStr)
            
            packetData=packetDataStr[onlyImageStartIndex: onlyImageEndIndex]
            imageNumber = 0;
            imagePacketNumber = 0;
            pointAssoc = 0;

            f.write(packetData)

        if (lineFromHC12.decode("utf-8").startswith("PointNumber")):
            print(lineFromHC12)

        i = i+1

except KeyboardInterrupt:
    print("Saving and closing...")
    f.close()
    exit()

print("Saving and closing...")
f.close()
exit()