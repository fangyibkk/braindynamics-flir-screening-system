from flirpy.camera.lepton import Lepton
import matplotlib.pyplot as plt
#import cv2

cam = Lepton()
image = cam.grab(device_id=1)
# print(image)

print('major_version',int.from_bytes(cam.major_version, byteorder='little'))
print('minor_version',int.from_bytes(cam.minor_version, byteorder='little'))
print('uptime_ms',cam.uptime_ms)
print('status',cam.status)
print('revision',cam.revision)
print('frame_count',cam.frame_count)
print('frame_mean',cam.frame_mean)
print('fpa_temp_k',cam.fpa_temp_k)
print('ffc_temp_k',cam.ffc_temp_k)
print('ffc_elapsed_ms',cam.ffc_elapsed_ms )
print('agc_roi',cam.agc_roi)
print('agc_clip_high',cam.agc_clip_high )
print('agc_clip_low',cam.agc_clip_low )
print('vudeo_format',cam.vudeo_format )

#cv2.imshow('sample', image)
plt.imsave('example.jpg', image[:60,:80])
plt.imshow(image[:60,:80])
plt.show()

cam.close()

