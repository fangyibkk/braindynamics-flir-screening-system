from flask import Flask, Response, render_template, send_from_directory, jsonify
from imutils.video import VideoStream
from threading import Lock
from time import sleep
from cv2 import imencode, imwrite
# im(age) write, im(age) encode

app = Flask(__name__)

# Global variable
outputFrame = None
lock = Lock()
vs = VideoStream(src=0).start()
sleep(2.0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/public/<path:path>')
def send_static(path):
    return send_from_directory('public', path)


def generate():
    global outputFrame, lock

    while True:
        outputFrame = vs.read()
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = imencode(".jpg", outputFrame)

            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/capture', methods=['GET'])
def capture():
    print('GET capture receive')
    with lock:
        image = vs.read()
    imwrite('capture/sample.jpg', image)
    return jsonify(success=True)
     

if __name__ == '__main__':
    app.run()

vs.stop()
