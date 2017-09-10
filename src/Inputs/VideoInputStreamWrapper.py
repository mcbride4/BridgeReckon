import cv2
import numpy as np


class VideoInputStreamWrapper():
    def __init__(self, camera):
        self.camera = cv2.VideoCapture(camera)

    def get_every_two_sec(self, n):
        m = 0
        while m != n:
            ret, frame = self.camera.cap.read()
            m += 1
        to_ret_frame = np.asarray(frame[0][:][:]).reshape((1080, 1920))
        return to_ret_frame
