from flask import Flask, Response, render_template, send_from_directory, jsonify
from imutils.video import VideoStream
from threading import Lock, Thread
from time import sleep
import os
import cv2 as cv

# Global variable
output_frame = None
output_lepton_frame = None
lock = Lock()

vs = cv.VideoCapture(2)
lepton = cv.VideoCapture(0)
#vs.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M','J','P','G'))
#lepton.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('R','G','B','P'))

# Constant
HAAR_CASCADE_PATH = 'model/haarcascade_frontalface_alt.xml'

app = Flask(__name__)
sleep(2.0)

def detect_face():

    global vs, output_frame
    
    process_this_frame = True
    scale=0.25
    rectangle = { 'top':0, 'bottom':0, 'left':0, 'right':0 }
    face_cascade = cv.CascadeClassifier()

    if not face_cascade.load(cv.samples.findFile(HAAR_CASCADE_PATH)):
        print('--(!)Error loading face cascade')
        exit(0)

    while True:
        if process_this_frame:
            can_read, frame = vs.read()
            if can_read:
                small_frame = cv.resize(frame, (0, 0), fx=scale, fy=scale)
                
                frame_gray = cv.cvtColor(small_frame, cv.COLOR_BGR2GRAY)
                frame_gray = cv.equalizeHist(frame_gray)
                faces = face_cascade.detectMultiScale(frame_gray)

                for (x,y,w,h) in faces:
                    #print(x,y,w,h)
                    inverted_scale = int(1/scale)
                    rectangle['left'] = x*inverted_scale
                    rectangle['bottom'] = y*inverted_scale
                    rectangle['right'] = rectangle['left'] + w*inverted_scale
                    rectangle['top'] = rectangle['bottom'] + h*inverted_scale
                    #print(rectangle['top'],rectangle['left'],rectangle['right'],rectangle['bottom'])

        # cv override frame
        cv.rectangle(frame, (rectangle['left'], rectangle['top']), (rectangle['right'], rectangle['bottom']), (0, 0, 255), 2)
        # default VideoStream() resolution=320 x 240
        #cv.line(frame, (0,120), (320,120), (0,0,0), 5)
        process_this_frame = not process_this_frame

        with lock:
            output_frame = frame.copy()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/public/<path:path>')
def send_static(path):
    return send_from_directory('public', path)


def generate():
    global output_frame, lock

    while True:
        #output_frame = vs.read()
        with lock:
            if output_frame is None:
                continue
            #output_frame = cv.resize(output_frame, (0, 0), fx=0.5, fy=0.5)
            (flag, encodedImage) = cv.imencode(".jpg", output_frame)

            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

#def lepton_generate():
#    global output_lepton_frame
#
#    while True:
#        _, output_lepton_frame = lepton.read()
#        if output_lepton_frame is None:
#            continue
#        (flag, encodedImage) = cv.imencode(".jpg", output_lepton_frame)
#
#        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route('/picamera_feed')
def picamera_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

#@app.route('/lepton_feed')
#def lepton_feed():
#    return Response(lepton_generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/capture/<username>', methods=['GET'])
def capture(username):
    print('GET capture receive')
    subdirectory = 'capture/%s' % username
    for i in range(5):
        with lock:
            _, image = vs.read()
            can_read_flir_image, flir_image = lepton.read()
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)
        cv.imwrite('%s/%s-%s.jpg' % (subdirectory, username, i), image)
        if can_read_flir_image:
            cv.imwrite('%s/flir-%s-%s.jpg' % (subdirectory, username, i), flir_image)
    return jsonify(fileList=os.listdir(subdirectory))
     

if __name__ == '__main__':
    thread = Thread(target=detect_face)
    thread.daemon = True
    thread.start()
    app.run()

vs.release()
lepton.release()
