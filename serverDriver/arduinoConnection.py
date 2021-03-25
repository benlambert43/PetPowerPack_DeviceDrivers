import serial
import platform
import mysql.connector
import dbEnvConnectors
import pathlib
import base64


def arduinoEngine():

  print("[THREAD 1]: Entered arduino thread.")

  # Environment Variables
  CURRENT_PLATFORM = platform.system()
  SERIAL_PORT = ''

  # Detect which serial file reader to use
  if (CURRENT_PLATFORM == 'Linux'):
      SERIAL_PORT = '/dev/ttyUSB0'
  elif (CURRENT_PLATFORM == 'Windows'):
      SERIAL_PORT = 'COM3'


  # Connect to Arduino over serial port
  arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=100)
  completeImagePackets = 0
  imageBuffer = ""

  while True:
    lineFromHC12 = arduino.readline()


    try:
        if (lineFromHC12.decode("utf-8").startswith("imageNumber")):

            dbIMG = mysql.connector.connect(
                host=dbEnvConnectors.getDB().host,
                user=dbEnvConnectors.getDB().user,
                password=dbEnvConnectors.getDB().password,
                database="petpowerpacksessiondata"
            )
            imgcursor = dbIMG.cursor()
            
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
                # print("Entire image complete.")
                pathToIMG = str(pathlib.Path().absolute()) + "\\imageCache\\" + str(currentTime.strip()) + ".jpg"
                # print(pathToIMG)
                with open(pathToIMG, "wb") as fh:
                    fh.write(base64.b64decode(imageBuffer))
                imageBuffer = ""
            
            
            imgcursor.execute("INSERT INTO petpowerpacksessiondata.image (imageNumber, imagePacketNumber, packetData, pointAssoc, packetTimeStamp) VALUES(%s, %s, %s, %s, %s);", (int(imageNumber),int(imagePacketNumber),packetData,int(imageNumber),currentTime))
            dbIMG.commit()
            imgcursor.close()
            dbIMG.close()


        if (lineFromHC12.decode("utf-8").startswith("PointNumber")):
            lineFromHC12Str = lineFromHC12.decode('utf-8')

            db = mysql.connector.connect(
                host=dbEnvConnectors.getDB().host,
                user=dbEnvConnectors.getDB().user,
                password=dbEnvConnectors.getDB().password,
                database="petpowerpacksessiondata"
            )
            cursor = db.cursor()

            if lineFromHC12Str.__contains__("GPS:"):
                lineFromHC12Str = lineFromHC12Str.strip()
                pointNumForGPS = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("GPS: ")].strip()
                finalGPSstr = lineFromHC12Str[lineFromHC12Str.rfind(" GPS: ") + len(" GPS: "): len(lineFromHC12Str)].strip()
                #print("GPS STRING FOR " + pointNumForGPS + " : " + finalGPSstr)
                cursor.execute("INSERT INTO petpowerpacksessiondata.gps (gpsPointNumber, gpsCoords, gpsImageLength, gpsExpectedPackets, gpsTime) VALUES(%s, %s, NULL, NULL, NULL);", (pointNumForGPS, finalGPSstr))
                db.commit()

            if lineFromHC12Str.__contains__("IMG Length:"):
                lineFromHC12Str = lineFromHC12Str.strip()
                pointNumForImgLen = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("IMG Length: ")].strip()
                finalImgLenstr = lineFromHC12Str[lineFromHC12Str.rfind(" IMG Length: ") + len(" IMG Length: "): len(lineFromHC12Str)].strip()
                #print("ImgLen STRING FOR " + pointNumForImgLen + " : " + finalImgLenstr)
                cursor.execute("UPDATE petpowerpacksessiondata.gps SET gpsImageLength=%s WHERE gpsPointNumber=%s;",(finalImgLenstr, pointNumForImgLen))
                db.commit()

            if lineFromHC12Str.__contains__("videoFeed:"):
                lineFromHC12Str = lineFromHC12Str.strip()
                pointNumForVideoFeed = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("videoFeed: ")].strip()
                finalVideoFeedstr = lineFromHC12Str[lineFromHC12Str.rfind(" videoFeed: ") + len(" videoFeed: "): len(lineFromHC12Str)].strip()
                # print("VideoFeed STRING FOR " + pointNumForVideoFeed + " : " + finalVideoFeedstr)
                cursor.execute("UPDATE petpowerpacksessiondata.gps SET gpsVideoFeed=%s WHERE gpsPointNumber=%s;",(finalVideoFeedstr, pointNumForVideoFeed))
                db.commit()

            if lineFromHC12Str.__contains__("Expected Packets:"):
                lineFromHC12Str = lineFromHC12Str.strip()
                pointNumForExpectedPackets = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("Expected Packets: ")].strip()
                finalExpectedPacketsstr = lineFromHC12Str[lineFromHC12Str.rfind(" Expected Packets: ") + len(" Expected Packets: "): len(lineFromHC12Str)].strip()
                #print("ExpectedPackets STRING FOR " + pointNumForExpectedPackets + " : " + finalExpectedPacketsstr)
                cursor.execute("UPDATE petpowerpacksessiondata.gps SET gpsExpectedPackets=%s WHERE gpsPointNumber=%s;",(finalExpectedPacketsstr, pointNumForExpectedPackets))
                completeImagePackets = int(finalExpectedPacketsstr)
                db.commit()

            if lineFromHC12Str.__contains__("Time:"):
                lineFromHC12Str = lineFromHC12Str.strip()
                pointNumForTime = lineFromHC12Str[lineFromHC12Str.rfind("PointNumber: ") + len("PointNumber: "): lineFromHC12Str.rfind("Time: ")].strip()
                finalTimestr = lineFromHC12Str[lineFromHC12Str.rfind(" Time: ") + len(" Time: "): len(lineFromHC12Str)].strip()
                #print("Time STRING FOR " + pointNumForTime + " : " + finalTimestr)
                cursor.execute("UPDATE petpowerpacksessiondata.gps SET gpsTime=%s WHERE gpsPointNumber=%s;",(finalTimestr, pointNumForTime))
                db.commit()
    except:
        continue

