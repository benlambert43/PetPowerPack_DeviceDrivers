#include <SoftwareSerial.h>

SoftwareSerial HC12(10, 11); // HC-12 TX Pin, HC-12 RX Pin
SoftwareSerial gps(2, 3);

char byteIn;                                        // Temporary variable
String SerialReadBuffer = "";                       // Read/Write Buffer
String GPSReadBuffer = "";                          // Read/Write Buffer

boolean serialEnd = false;                          // Flag for End of Serial String
boolean GPSEnd = false;                             // Flag for End of GPS String

void setup() {

  SerialReadBuffer.reserve(64999);                     // Reserve 82 bytes for message
  GPSReadBuffer.reserve(82);                         // Reserve 82 bytes for longest NMEA sentence

  delay(80);

  Serial.begin(9600);
  HC12.begin(9600);
  gps.begin(9600);
  HC12.write("initializing...\n");

  delay(80);

}

void loop() {

  while (gps.available()) {
    char filter = gps.read();
    if (isPunct(filter) || isDigit(filter) || (filter == '\n') || isUpperCase(filter) || (filter == '*') ) {
      byteIn = filter;
      GPSReadBuffer += char(byteIn);
      if (byteIn == '\n') {
        GPSEnd = true;
      }
    }
    else {
      GPSEnd = true;
      break;
    }
  }

  while (Serial.available()) {                      // If Serial monitor has data
    byteIn = Serial.read();                         // Store each character in byteIn
    SerialReadBuffer += char(byteIn);               // Write each character of byteIn to SerialReadBuffer
    if (byteIn == '\n') {                           // At the end of the line
      serialEnd = true;                             // Set serialEnd flag to true.
    }
  }




  if (GPSEnd) {

    if (GPSReadBuffer.startsWith("$GPRMC")) {
      GPSReadBuffer += char('\n');
      HC12.print(GPSReadBuffer);
      Serial.print(GPSReadBuffer);
    }

    GPSReadBuffer = "";
    GPSEnd = false;                                 // Reset GPS

    if (serialEnd) {
      HC12.print(SerialReadBuffer);
      SerialReadBuffer = "";
      serialEnd = false;
    }

  }




}
