#include <SoftwareSerial.h>

// The serial connection to the GPS module
SoftwareSerial gps(2, 3);
SoftwareSerial HC12(10, 11);

void setup() {
  Serial.begin(9600);
  gps.begin(9600);
}

void loop() {

  String payload = "";
  int payloadLen = 0;
  char gpsData;
  
  while (gps.available() > 0) {

    // get the byte data from the GPS
    gpsData = gps.read();
    // build the payload

  }
  payload += gpsData;
  payloadLen++;
  
  if (payloadLen > 0) {
    Serial.print(payload);
  }
}
