from VideoInputWrapper import VideoInputWrapper
#
# if __name__ == '__main__':
#     video = VideoInputWrapper('/home/ubuntu/Desktop/MOV3_CV.AVI')
#     success, image = video.vidcap.read()
#     print(image)
import tkinter

import numpy as np
import skvideo.io
from matplotlib import pyplot as plt

cap = VideoInputWrapper('/home/ubuntu/Desktop/MOV3_CV.avi')
for i in range(0, 20):
    plt.imshow(np.asarray(cap.return_every_n_frame(100)))
    plt.show()