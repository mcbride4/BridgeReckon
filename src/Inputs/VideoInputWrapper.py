import skvideo.io
import numpy as np


class VideoInputWrapper(object):
    def __init__(self, device=0):
        self.device = device
        self.vidcap = skvideo.io.vreader(self.device, as_grey=True)

    def return_every_n_frame(self, n):
        m = n
        for frame in self.vidcap:
            n += -1
            if n == 0:
                n = m
                to_ret_frame = np.asarray(frame[0][:][:]).reshape((1080, 1920))
                return to_ret_frame
