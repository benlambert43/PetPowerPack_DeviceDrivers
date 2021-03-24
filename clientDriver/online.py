from flask import Flask, render_template, Response
import cv2
import socket

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

def onlineVideoFeed(camera): 
  app = Flask(__name__)

  def gen_frames():
      while True:
          success, frame = camera.read()
          if not success:
              break
          else:
              ret, buffer = cv2.imencode('.jpg', frame)
              frame = buffer.tobytes()
              yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


  @app.route('/video_feed')
  def video_feed():
      #Video streaming route. Put this in the src attribute of an img tag
      return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


  @app.route('/')
  def index():
      """Video streaming home page."""
      return render_template('index.html')

  ipAddr = get_ip()
  app.run(host=ipAddr,port=8089)