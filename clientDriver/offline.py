import cv2
from PIL import Image
import io
import base64
import math
import time
import socket
from datetime import datetime



def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def offlineThread(write, readFromSerial, camera, detectInternet):
  dt = datetime.now()
  i = int(dt.strftime("%Y%m%d%H%M%S"))

  print("[T1]: Offline Thread Running:")

  while(True):

    ret, frame = camera.read() 
    cv2.imwrite('capture.jpg', frame)

    image = Image.open('capture.jpg')
    image.thumbnail((120, 120))
    image.save('opt1.jpg')

    optimizedImage2 = Image.open('opt1.jpg')
    output = io.BytesIO()
    optimizedImage2.save(output, format="jpeg")
    jpg_as_text = base64.b64encode(output.getvalue()) 
    imgString = jpg_as_text.decode('utf-8')
    ipAddr = get_ip()


    gpsCoords = readFromSerial();
    print(gpsCoords)


    try:
        gpsCoords = gpsCoords.decode('utf-8')
    except:
        continue;

    print(gpsCoords)
    
    write("PointNumber: " + str(i) + " GPS: " + gpsCoords)
    write("PointNumber: " + str(i) + " IMG Length: " + str(len(imgString)))
    write("PointNumber: " + str(i) + " Expected Packets: " + str(math.ceil(len(imgString) / 750)))
    gpsT = time.localtime()
    gpsCurrentTime = time.strftime("%m-%d-%Y %H-%M-%S", gpsT)
    write("PointNumber: " + str(i) + " Time: " + str(gpsCurrentTime))
    write("PointNumber: " + str(i) + " videoFeed: " + str(ipAddr + ':8089/video_feed'))


    

    imgSegmentOffset = 0
    packets = 0

 

    if (not(detectInternet())):

      # print("No Internet.")

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
        
      dt = datetime.now()
      i = int(dt.strftime("%Y%m%d%H%M%S"))

  

    else:
      # print("Internet detected, skipping.")
      dt = datetime.now()
      i = int(dt.strftime("%Y%m%d%H%M%S"))
      time.sleep(1)
      continue
