import dbEnvConnectors
import mysql.connector

def mysqlinitsetup():

  # Connect to the local MySQL DB
  print("Checking for database on " + dbEnvConnectors.getDB().host + "...")
  mydbconnection1 = mysql.connector.connect(
    host=dbEnvConnectors.getDB().host,
    user=dbEnvConnectors.getDB().user,
    password=dbEnvConnectors.getDB().password
  )

  # Initialize the cursor opject on the database
  mycursor = mydbconnection1.cursor()


  # Find out if the petpowerpacksessiondata already exists on the server.
  # If it doesn't, drop it and create it again.
  # The database only contains data for the current session, more permanent data will be stored on a seperate database.

  mycursor.execute("SHOW DATABASES")
  dbArray = []
  for x in mycursor:
      dbArray.append(str(x))

  alreadyContainsDB = False;
  for dbstr in dbArray:
      normalizeStr = str(dbstr)
      if (normalizeStr.__contains__("petpowerpacksessiondata")):
          alreadyContainsDB = True;

  if (not(alreadyContainsDB)):
      print("Creating petpowerpacksessiondata...")
      create_db_query = "CREATE DATABASE petpowerpacksessiondata"
      mycursor.execute(create_db_query)
  else:
      print("Refreshing and connecting.")
  mydbconnection1.commit()
  mycursor.close()
  mydbconnection1.close()


  print("Connecting to db on " + dbEnvConnectors.getDB().host + "...")
  mydb = mysql.connector.connect(
  host=dbEnvConnectors.getDB().host,
  user=dbEnvConnectors.getDB().user,
  password=dbEnvConnectors.getDB().password,
  database="petpowerpacksessiondata"
  )

  mysqlCmdCursor = mydb.cursor()

  createTableCommandGPS = 'CREATE TABLE IF NOT EXISTS `gps` (`gpsPointNumber` bigint unsigned NOT NULL, `gpsCoords` varchar(2048) CHARACTER SET utf8_general_ci COLLATE utf8_general_ci NOT NULL, `gpsImageLength` int DEFAULT NULL, `gpsExpectedPackets` int DEFAULT NULL, `gpsVideoFeed` varchar(255) DEFAULT NULL, `gpsTime` varchar(255) DEFAULT NULL, PRIMARY KEY (`gpsPointNumber`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8_general_ci COLLATE=utf8_general_ci'
  mysqlCmdCursor.execute(createTableCommandGPS)

  createTableCommandImage = 'CREATE TABLE IF NOT EXISTS `image` ( `imageID` bigint unsigned NOT NULL AUTO_INCREMENT, `imageNumber` bigint unsigned NOT NULL, `imagePacketNumber` bigint unsigned NOT NULL, `packetData` varchar(2048) DEFAULT NULL, `pointAssoc` bigint unsigned NOT NULL, `packetTimeStamp` varchar(100) DEFAULT NULL, PRIMARY KEY (`imageID`), KEY `image_FK` (`pointAssoc`), CONSTRAINT `image_FK` FOREIGN KEY (`pointAssoc`) REFERENCES `gps` (`gpsPointNumber`) ON DELETE CASCADE ON UPDATE CASCADE ) ENGINE=InnoDB DEFAULT CHARSET=utf8_general_ci COLLATE=utf8_general_ci'
  mysqlCmdCursor.execute(createTableCommandImage)
  mydb.commit() 
  mysqlCmdCursor.close()
  mydb.close()


  print("Connected to db on localhost.")