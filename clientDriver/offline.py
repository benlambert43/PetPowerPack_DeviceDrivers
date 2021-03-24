import cv2
from PIL import Image
import io
import base64
import math
import time



def offlineThread(write, readFromSerial, camera, detectInternet):

  i = 0;
  print("Starting Client...")


  while(True):

    if (not(detectInternet())):
      try:
        print("No Internet.")
        
        
        ret, frame = camera.read() 
        cv2.imwrite('capture.jpg', frame)

        image = Image.open('capture.jpg')
        image.thumbnail((120, 120))
        image.save('opt1.jpg')

        optimizedImage2 = Image.open('opt1.jpg')

        output = io.BytesIO()
        optimizedImage2.save(output, format="jpeg")
        image_as_string = base64.b64encode(output.getvalue()) 

        jpg_as_text = image_as_string



        gpsCoords = readFromSerial();
        imgString = jpg_as_text.decode('utf-8')
        try:
            gpsCoords = gpsCoords.decode('utf-8')

            # on bootup it displays starting client in serial. We want to ignore this and read the next line which contains GPS data.
            if "STARTING CLIENT" in gpsCoords:
                print(gpsCoords)
                gpsCoords = readFromSerial();
                gpsCoords = gpsCoords.decode('utf-8')
        except:
            continue;


        
        write("PointNumber: " + str(i) + " GPS: " + gpsCoords)
        

        write("PointNumber: " + str(i) + " IMG Length: " + str(len(imgString)))
        

        write("PointNumber: " + str(i) + " Expected Packets: " + str(math.ceil(len(imgString) / 750)))
        

        gpsT = time.localtime()
        gpsCurrentTime = time.strftime("%m-%d-%Y %H-%M-%S", gpsT)
        write("PointNumber: " + str(i) + " Time: " + str(gpsCurrentTime))
        

        imgSegmentOffset = 0
        packets = 0
        while (True):
            t = time.localtime()
            currentTime = time.strftime("%m-%d-%Y %H-%M-%S", t)

            if (imgSegmentOffset + 750 > len(imgString)):
                terminatingString = imgString[imgSegmentOffset: len(imgString)]
                terminatingStringPayload = "imageNumber: " + str(i) + " imagePacketNumber: " + str(packets) + " currentTime: " + str(currentTime) + " packetData: " + terminatingString
                write(terminatingStringPayload)
                
                # print(terminatingStringPayload)
                # print("Finished sending image with " + str(packets) + " packets.")
                
                break;
            else:
                partialImgString = imgString[imgSegmentOffset: imgSegmentOffset + 750]
                partialImgStringPayload = "imageNumber: " + str(i) + " imagePacketNumber: " + str(packets)  + " currentTime: " + str(currentTime) +  " packetData: " + partialImgString
                write(partialImgStringPayload)
                
                # print(partialImgStringPayload)
                imgSegmentOffset = imgSegmentOffset + 750
                packets = packets + 1

        i = i+1
      except:
          continue
    else:
      print("Internet detected, skipping.")
      time.sleep(3)
      continue