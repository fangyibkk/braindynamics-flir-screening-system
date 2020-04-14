from flirpy.camera.lepton import Lepton
import cv2

cam = Lepton()
image = cam.grab(device_id=0)

cv2.imshow('sample', image)
cam.close()

