import serial
import platform
import dbEnvConnectors
import mysql.connector
import pathlib
import base64
from datetime import date, datetime

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
print("Checking for database on " + dbEnvConnectors.getDB().host + "...")
mydbconnection1 = mysql.connector.connect(
  host=dbEnvConnectors.getDB().host,
  user=dbEnvConnectors.getDB().user,
  password=dbEnvConnectors.getDB().password
)

# Initialize the cursor opject on the database
mycursor = mydbconnection1.cursor()


# Find out if the petpowerpackserverdb already exists on the server.
# If it doesn't, drop it and create it again.
# The database only contains data for the current session, more permanent data will be stored on a seperate database.

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
    deletequery = "DROP DATABASE petpowerpackserverdb"
    mycursor.execute(deletequery)
    create_db_query = "CREATE DATABASE PetPowerPackServerDB"
    mycursor.execute(create_db_query)
    print("Refreshing and connecting.")
mydbconnection1.commit()
mycursor.close()
mydbconnection1.close()


print("Connecting to db on " + dbEnvConnectors.getDB().host + "...")
mydb = mysql.connector.connect(
  host=dbEnvConnectors.getDB().host,
  user=dbEnvConnectors.getDB().user,
  password=dbEnvConnectors.getDB().password,
  database="petpowerpackserverdb"
)

mysqlCmdCursor = mydb.cursor()

createTableCommandGPS = 'CREATE TABLE IF NOT EXISTS `gps` (`gpsPointNumber` bigint unsigned NOT NULL, `gpsCoords` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, `gpsImageLength` int DEFAULT NULL, `gpsExpectedPackets` int DEFAULT NULL, `gpsTime` varchar(255) DEFAULT NULL, PRIMARY KEY (`gpsPointNumber`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
mysqlCmdCursor.execute(createTableCommandGPS)

createTableCommandImage = 'CREATE TABLE IF NOT EXISTS `image` ( `imageID` bigint unsigned NOT NULL AUTO_INCREMENT, `imageNumber` bigint unsigned NOT NULL, `imagePacketNumber` bigint unsigned NOT NULL, `packetData` varchar(2048) DEFAULT NULL, `pointAssoc` bigint unsigned NOT NULL, `packetTimeStamp` varchar(100) DEFAULT NULL, PRIMARY KEY (`imageID`), KEY `image_FK` (`pointAssoc`), CONSTRAINT `image_FK` FOREIGN KEY (`pointAssoc`) REFERENCES `gps` (`gpsPointNumber`) ON DELETE CASCADE ON UPDATE CASCADE ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
mysqlCmdCursor.execute(createTableCommandImage)
mydb.commit() 
mysqlCmdCursor.close()
mydb.close()

i = 0
completeImagePackets = 0
imageBuffer = ""
print("Connected to db on localhost.")


try:
    while True:
        lineFromHC12 = arduino.readline()
        try:

            if (lineFromHC12.decode("utf-8").startswith("imageNumber")):

                dbIMG = mysql.connector.connect(
                    host=dbEnvConnectors.getDB().host,
                    user=dbEnvConnectors.getDB().user,
                    password=dbEnvConnectors.getDB().password,
                    database="petpowerpackserverdb"
                )
                imgcursor = dbIMG.cursor()
                

                # DATA FORMAT:
                # "imageNumber: " + str(i) + " imagePacketNumber: " + str(packets)  + " currentTime: " + str(currentTime) +  " packetData: " + partialImgString


                # packetData:
                packetDataStr = lineFromHC12.decode("utf-8")
                onlyImageStartIndex = packetDataStr.rfind("packetData:")
                onlyImageEndIndex = len(packetDataStr)
                packetData=packetDataStr[(onlyImageStartIndex  + (len("packetData: "))): onlyImageEndIndex]

                # imageNumber:
                imageNumber = "";
                imgNumStart = packetDataStr.rfind("imageNumber: ")
                imgNumEnd = imgNumStart + len("imageNumber: ")

                # imagePacketNumber:
                imagePacketNumber = "";
                packetDataStr.rfind("imagePacketNumber: ")
                imgPackNumStart = packetDataStr.rfind("imagePacketNumber: ")
                imgPackNumEnd = imgPackNumStart + len("imagePacketNumber: ")

                # currentTime
                currentTime = "";
                packetDataStr.rfind("currentTime: ")
                imgCurrTimeStart = packetDataStr.rfind("currentTime: ")
                imgCurrTimeEnd = imgCurrTimeStart + len("currentTime: ")


                imageNumber = str(packetDataStr[imgNumEnd: imgPackNumStart]).strip()
                #print(imageNumber)

                imagePacketNumber = str(packetDataStr[imgPackNumEnd: imgCurrTimeStart]).strip()
                #print(imagePacketNumber)


                currentTime = str(packetDataStr[imgCurrTimeEnd: onlyImageStartIndex]).strip()
                #print(currentTime)
                
                #f.write(packetData)
                imageBuffer = imageBuffer + packetData.strip()

                if ((int(imagePacketNumber)+1) == int(completeImagePackets)):
                    dt_string = datetime.now().strftime("%m-%d-%Y %H-%M-%S")


                    print("Entire image complete.")
                    pathToIMG = str(pathlib.Path().absolute()) + "\\imageCache\\" + str(dt_string.strip()) + ".jpg"
                    print(pathToIMG)
                    with open(pathToIMG, "wb") as fh:
                        fh.write(base64.b64decode(imageBuffer))
                    imageBuffer = ""
                
                
                imgcursor.execute("INSERT INTO petpowerpackserverdb.image (imageNumber, imagePacketNumber, packetData, pointAssoc, packetTimeStamp) VALUES(%s, %s, %s, %s, %s);", (int(imageNumber),int(imagePacketNumber),packetData,int(imageNumber),currentTime))
                dbIMG.commit()
                imgcursor.close()
                dbIMG.close()


            if (lineFromHC12.decode("utf-8").startswith("PointNumber")):
                lineFromHC12Str = lineFromHC12.decode('utf-8')

                # write("PointNumber: " + str(i) + " GPS: " + gpsCoords)
                # write("PointNumber: " + str(i) + " IMG Length: " + str(len(imgString)))
                # write("PointNumber: " + str(i) + " Expected Packets: " + str(math.ceil(len(imgString) / 512)))
                # write("PointNumber: " + str(i) + " Time: " + str(gpsCurrentTime))

                db = mysql.connector.connect(
                    host=dbEnvConnectors.getDB().host,
                    user=dbEnvConnectors.getDB().user,
                    password=dbEnvConnectors.getDB().password,
                    database="petpowerpackserverdb"
                )
                cursor = db.cursor()

                if lineFromHC12Str.__contains__("GPS:"):
                    lineFromHC12Str = lineFromHC12Str.strip()
                    pointNumForGPS = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("GPS: ")].strip()
                    finalGPSstr = lineFromHC12Str[lineFromHC12Str.rfind(" GPS: ") + len(" GPS: "): len(lineFromHC12Str)].strip()
                    #print("GPS STRING FOR " + pointNumForGPS + " : " + finalGPSstr)
                    cursor.execute("INSERT INTO petpowerpackserverdb.gps (gpsPointNumber, gpsCoords, gpsImageLength, gpsExpectedPackets, gpsTime) VALUES(%s, %s, NULL, NULL, NULL);", (pointNumForGPS, finalGPSstr))
                    db.commit()

                if lineFromHC12Str.__contains__("IMG Length:"):
                    lineFromHC12Str = lineFromHC12Str.strip()
                    pointNumForImgLen = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("IMG Length: ")].strip()
                    finalImgLenstr = lineFromHC12Str[lineFromHC12Str.rfind(" IMG Length: ") + len(" IMG Length: "): len(lineFromHC12Str)].strip()
                    #print("ImgLen STRING FOR " + pointNumForImgLen + " : " + finalImgLenstr)
                    cursor.execute("UPDATE petpowerpackserverdb.gps SET gpsImageLength=%s WHERE gpsPointNumber=%s;",(finalImgLenstr, pointNumForImgLen))
                    db.commit()

                if lineFromHC12Str.__contains__("Expected Packets:"):
                    lineFromHC12Str = lineFromHC12Str.strip()
                    pointNumForExpectedPackets = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("Expected Packets: ")].strip()
                    finalExpectedPacketsstr = lineFromHC12Str[lineFromHC12Str.rfind(" Expected Packets: ") + len(" Expected Packets: "): len(lineFromHC12Str)].strip()
                    #print("ExpectedPackets STRING FOR " + pointNumForExpectedPackets + " : " + finalExpectedPacketsstr)
                    cursor.execute("UPDATE petpowerpackserverdb.gps SET gpsExpectedPackets=%s WHERE gpsPointNumber=%s;",(finalExpectedPacketsstr, pointNumForExpectedPackets))
                    completeImagePackets = int(finalExpectedPacketsstr)
                    db.commit()

                if lineFromHC12Str.__contains__("Time:"):
                    lineFromHC12Str = lineFromHC12Str.strip()
                    pointNumForTime = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("Time: ")].strip()
                    finalTimestr = lineFromHC12Str[lineFromHC12Str.rfind(" Time: ") + len(" Time: "): len(lineFromHC12Str)].strip()
                    #print("Time STRING FOR " + pointNumForTime + " : " + finalTimestr)
                    cursor.execute("UPDATE petpowerpackserverdb.gps SET gpsTime=%s WHERE gpsPointNumber=%s;",(finalTimestr, pointNumForTime))
                    db.commit()
                
                cursor.close()
                db.close()


        except:
            continue

except KeyboardInterrupt:
    print("Saving and closing...")
    f.close()
    exit()

print("Saving and closing...")
f.close()
exit()