from flask import Flask, Response, jsonify, send_file
from threading import Lock, Thread, Event
from flirpy.camera.lepton import Lepton
from time import sleep
from math import sqrt
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import os, shutil

# Global constant
import project_config as PROJECT_CONFIG
from routes import views


# Global variable
output_frame = None
lock = Lock()
flir_count = 1
temp_scale = np.loadtxt(PROJECT_CONFIG.TEMPERATURE_CSV_PATH, delimiter=',')


# Set up external file/source
#vs = cv.VideoCapture(PROJECT_CONFIG.PI_CAMERA_NUMBER)
vs = cv.VideoCapture(PROJECT_CONFIG.GSTREAMER_STRING, cv.CAP_GSTREAMER)
sleep(2.0)


app = Flask(__name__, template_folder='./templates', static_folder='./public')
app.register_blueprint(views)


def detect_face():

    global vs, output_frame
    
    # local variable
    process_this_frame = True
    scale=0.25
    forehead = { 'top': int(28/60*480), 'bottom': int(32/60*480), 'left': int(38/80*640),'right': int(42/80*640) }
    rectangle = { 'top':0, 'bottom':0, 'left':0, 'right':0 }
    face_cascade = cv.CascadeClassifier()

    if not face_cascade.load(cv.samples.findFile(PROJECT_CONFIG.HAAR_CASCADE_PATH)):
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
                    inverted_scale = int(1/scale)
                    rectangle['left'] = x*inverted_scale
                    rectangle['bottom'] = y*inverted_scale
                    rectangle['right'] = rectangle['left'] + w*inverted_scale
                    rectangle['top'] = rectangle['bottom'] + h*inverted_scale

        # WARNING: cv modify frame pass to the function
        cv.rectangle(frame, (rectangle['left'], rectangle['top']), (rectangle['right'], rectangle['bottom']), (0, 0, 255), 2)
        cv.rectangle(frame, (forehead['left'], forehead['top']), (forehead['right'], forehead['bottom']), (0, 255, 0), 2)
        # NOTE: Default VideoStream() resolution=320 x 240
        process_this_frame = not process_this_frame

        with lock:
            output_frame = frame.copy()

def setup_empty_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        shutil.rmtree(dir_path)
        os.makedirs(dir_path)
    return


def generate():
    global output_frame, lock

    while True:
        #output_frame = vs.read()
        with lock:
            if output_frame is None:
                continue
            (flag, encodedImage) = cv.imencode(".jpg", output_frame)

            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route('/picamera_feed')
def picamera_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# For capture and save thermal image for show at <img src=/>
@app.route('/capture_thermal')
def capture_thermal():

    global flir_count

    # local variable
    lookup_temp = 35
    subdirectory = 'capture/flir-current'
    filename = '%s/flir-current-%s.jpg' % (subdirectory, flir_count)
    filename_roi = '%s/flir-current-roi-%s.jpg' % (subdirectory, flir_count)

    # setup camera per request
    lepton = Lepton()
    sleep(1)

    setup_empty_dir(subdirectory)
    print('GET received, start capture thermal')
    flir_image = lepton.grab(device_id=PROJECT_CONFIG.LEPTON_CAMERA_NUMBER)
    print("Working")
    forehead_roi = flir_image[38:42, 28:32]
    #forehead_roi_gray = np.asarray(cv.cvtColor(forehead_roi, cv.COLOR_BGR2GRAY))
    forehead_roi_mean = np.mean(forehead_roi)

    #################
    ### TODO HERE ###
    #lookup_temp = temp_scale[int(forehead_roi_mean)]
    #################

    print("Mean value is " + str(forehead_roi_mean))
    print("lookup temp is " + str(lookup_temp))
    plt.imsave(filename, flir_image[:60,:80])
    plt.imsave(filename_roi, forehead_roi)
    print("Write success: " + str(filename))
    lepton.close()
    flir_count += 1
    return jsonify(frame_num=(flir_count-1), temp=lookup_temp)

# For setting new img src
@app.route('/get_thermal/<frame_num>')
def get_thermal(frame_num):
    print('GET capture thermal frame num: ' + str(frame_num))
    subdirectory = 'capture/flir-current'
    filename = '%s/flir-current-%s.jpg' % (subdirectory, frame_num)
    return send_file(filename, mimetype='image/jpg')

if __name__ == '__main__':
    thread = Thread(target=detect_face)
    thread.daemon = True
    thread.start()
    app.run()

vs.release()
