import serial
import platform
import cv2
import base64
import time
from PIL import Image
import io


CURRENT_PLATFORM = platform.system()
SERIAL_PORT = ''
camera = cv2.VideoCapture(0)



if (CURRENT_PLATFORM == 'Linux'):
    SERIAL_PORT = '/dev/ttyUSB0'
elif (CURRENT_PLATFORM == 'Windows'):
    SERIAL_PORT = 'COM4'


arduino = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=100)

def write(x):
    try:
        arduino.write(bytes(x+'\n', 'utf-8'))
        return True
    except:
        return False

def readFromSerial():
    line = arduino.readline()
    return line



i = 0;
while(True):

    ret, frame = camera.read() 
    cv2.imwrite('capture.jpg', frame)

    image = Image.open('capture.jpg')
    image.thumbnail((256, 256))
    image.save('opt1.jpg')


    optimizedImage1 = Image.open('opt1.jpg')
    optimizedImage1.save("opt2.jpg",optimize=True,quality=95)

    optimizedImage2 = Image.open('opt2.jpg')

    output = io.BytesIO()
    optimizedImage2.save(output, format="jpeg")
    image_as_string = base64.b64encode(output.getvalue()) 

    jpg_as_text = image_as_string



    gpsCoords = readFromSerial();
    imgString = str(jpg_as_text)
    print(i)
    write("PointNumber: " + str(i) + " GPS: " + str(gpsCoords) + " IMG Length: " + str(len(imgString)))
    time.sleep(1)

    imgSegmentOffset = 0
    packets = 0
    while (True):

        if (imgSegmentOffset + 512 > len(imgString)):
            terminatingString = imgString[imgSegmentOffset: len(imgString)]
            write(terminatingString)
            time.sleep(1.5)
            print(terminatingString)
            packets = packets + 1
            print("Finished sending image with " + str(packets) + " packets.")
            break;

        else:
            partialImgString = imgString[imgSegmentOffset: imgSegmentOffset + 512]
            write(partialImgString)
            time.sleep(1.5)
            print(partialImgString)
            imgSegmentOffset = imgSegmentOffset + 512
            packets = packets + 1

    i = i+1

