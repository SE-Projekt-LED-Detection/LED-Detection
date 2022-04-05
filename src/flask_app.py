from flask import Flask, Response
import cv2
import queue
import threading

app = Flask(__name__)
video = cv2.VideoCapture(1)

lock = threading.Lock()
last_frame = None

def read_webcam():
    global lock, last_frame
    while True:
        # read the current frame
        (grabbed, frame) = video.read()
        # if the frame was not grabbed, then we have reached the end
        # of the stream
        if not grabbed:
            break
        # if the frame needs to be displayed/saved, then clone it
        if True:
            with lock:
                last_frame = frame.copy()

@app.route('/')
def index():
    return "Default Message"

def update_frame():
    global lock, last_frame

def gen(video):
    global lock, last_frame
    while True:
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if last_frame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", last_frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global video
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # start a thread that will perform motion detection
    t = threading.Thread(target=read_webcam)
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host='0.0.0.0', port=2204, threaded=True)