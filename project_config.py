# ALL CONSTANT AND CONFIG
# ARE SET UP HERE
PI_CAMERA_NUMBER=0
LEPTON_CAMERA_NUMBER=1
HAAR_CASCADE_PATH = 'model/haarcascade_frontalface_alt.xml'
TEMPERATURE_CSV_PATH = 'model/temperature.csv'

# FOR JETSON NANO
CAPTURE_WIDTH=640,
CAPTURE_HEIGHT=360,
DISPLAY_WIDTH=640,
DISPLAY_HEIGHT=360,
FPS=30,
FLIP_METHOD=2,


GSTREAMER_STRING = ' '.join((
    "nvarguscamerasrc !",
    "video/x-raw(memory:NVMM),",
    "width=(int)%d," % CAPTURE_WIDTH,
    "height=(int)%d," % CAPTURE_HEIGHT,
    "format=(string)NV12,",
    "framerate=(fraction)%d/1 !" %FPS,
    "nvvidconv flip-method=%d !" %FLIP_METHOD,
    "video/x-raw, width=(int)%d," %DISPLAY_WIDTH,
    "height=(int)%d," %DISPLAY_HEIGHT,
    "format=(string)BGRx !",
    "videoconvert !",
    "video/x-raw, format=(string)BGR ! appsink"
))
