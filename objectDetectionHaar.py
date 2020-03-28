from __future__ import print_function
import cv2 as cv
import argparse

def detectAndDisplay(frame):
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray)

    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray)
    for (x,y,w,h) in faces:
        center = (x + w//2, y + h//2)
        frame = cv.ellipse(frame, center, (w//2, h//2), 0, 0, 360, (255, 0, 255), 4)

        #faceROI = frame_gray[y:y+h,x:x+w]
        #-- In each face, detect eyes
        #eyes = eyes_cascade.detectMultiScale(faceROI)
        #for (x2,y2,w2,h2) in eyes:
        #    eye_center = (x + x2 + w2//2, y + y2 + h2//2)
        #    radius = int(round((w2 + h2)*0.25))
        #    frame = cv.circle(frame, eye_center, radius, (255, 0, 0 ), 4)

    cv.imshow('Capture - Face detection', frame)

parser = argparse.ArgumentParser(description='Code for Cascade Classifier tutorial.')
parser.add_argument('--face_cascade', help='Path to face cascade.', default='data/haarcascades/haarcascade_frontalface_alt.xml')
#parser.add_argument('--eyes_cascade', help='Path to eyes cascade.', default='data/haarcascades/haarcascade_eye_tree_eyeglasses.xml')
parser.add_argument('--camera', help='Camera divide number.', type=int, default=0)
args = parser.parse_args()

face_cascade_name = args.face_cascade
#eyes_cascade_name = args.eyes_cascade

face_cascade = cv.CascadeClassifier()
#eyes_cascade = cv.CascadeClassifier()

#-- 1. Load the cascades
if not face_cascade.load(cv.samples.findFile(face_cascade_name)):
    print('--(!)Error loading face cascade')
    exit(0)
#if not eyes_cascade.load(cv.samples.findFile(eyes_cascade_name)):
#    print('--(!)Error loading eyes cascade')
#    exit(0)

camera_device = args.camera
#-- 2. Read the video stream
cap = cv.VideoCapture(camera_device)
if not cap.isOpened:
    print('--(!)Error opening video capture')
    exit(0)

process_this_frame = True
scale=0.25
rectangle  = { 'top':0, 'bottom':0, 'left':0, 'right':0 }
while True:
    ret, frame = cap.read()
    if frame is None:
        print('--(!) No captured frame -- Break!')
        break

    if process_this_frame:
        small_frame = cv.resize(frame, (0, 0), fx=scale, fy=scale)
        
        frame_gray = cv.cvtColor(small_frame, cv.COLOR_BGR2GRAY)
        frame_gray = cv.equalizeHist(frame_gray)
        faces = face_cascade.detectMultiScale(frame_gray)

        for (x,y,w,h) in faces:
            #print(x,y,w,h)
            inverted_scale = int(1/scale)
            rectangle['left'] = x*inverted_scale
            rectangle['bottom'] = y*inverted_scale
            rectangle['right'] = rectangle['left']+w*inverted_scale
            rectangle['top'] = rectangle['bottom']+h*inverted_scale


            print(rectangle['top'],rectangle['left'],rectangle['right'],rectangle['bottom'])
            #center = (x + w//2, y + h//2)
            #frame = cv.ellipse(frame, center, (w//2, h//2), 0, 0, 360, (255, 0, 255), 4)
    cv.rectangle(frame, (rectangle['left'], rectangle['top']), (rectangle['right'], rectangle['bottom']), (0, 0, 255), 2)
    cv.imshow('Capture - Face detection', frame)
    process_this_frame = not process_this_frame

    if cv.waitKey(10) == 27:
        break
