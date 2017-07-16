from matplotlib import pyplot as plt

from src.Inputs.VideoInputFileWrapper import VideoInputWrapper

cap = VideoInputWrapper('/home/ubuntu/Desktop/MOV3_CV.avi')
for i in range(0, 20):
    frame = cap.return_every_n_frame(100)
    plt.imshow(frame)
    plt.show()
