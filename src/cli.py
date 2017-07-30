# USAGE
# python cli_deprecated.py --save-model 1 --weights output/lenet_weights.hdf5
# python cli_deprecated.py --load-model 1 --weights output/lenet_weights.hdf5

import argparse
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from src.model_load import ModelPrep


def parse_args():
    global args
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--save-model", type=int, default=-1,
                    help="(optional) whether or not model should be saved to disk")
    ap.add_argument("-l", "--load-model", type=int, default=-1,
                    help="(optional) whether or not pre-trained model should be loaded")
    ap.add_argument("-w", "--weights", type=str,
                    help="(optional) path to weights file")
    args = vars(ap.parse_args())

parse_args()
model = ModelPrep(args).compile()

def sliding_window(image, stepSize, windowSize):
    # slide a window across the image
    for y in range(0, image.shape[0], int(stepSize)):
        for x in range(0, image.shape[1], int(stepSize)):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


# print(os.listdir('.'))
# vidcap = cv2.VideoCapture('MOV_0003.AVI')ce
# # v = vidcap.open('MOV_0003.AVI')
# # success,image = vidcap.read()
# # print(vidcap.isOpened())
# frame_names = []
#
# #success = True
# if vidcap.grab():
#     success, image = vidcap.retrieve()
# else:
#     success = False
# count = 0
# while success:
#     if vidcap.grab():
#         if not count % 100:
#             success, image = vidcap.retrieve()
#         else:
#             count += 1
#             continue
#     else:
#         success = False
#     print('Read a new frame: ', success)
#     lower_red = np.array([150, 200, 150])
#     upper_red = np.array([255, 255, 255])
#     mask1 = cv2.inRange(image, lower_red, upper_red)
#     cv2.imwrite("test_frames/frame%d.jpg" % count, mask1)  # save frame as JPEG file
#     frame_names.append('test_frames/frame%d.jpg' % count)
#     count += 1

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="Path to the image")
# args = vars(ap.parse_args())

# load the image and define the window width and height
# image = cv2.imread(args["image"])

test_frames = os.listdir("./test_frames")
size = 60
(winW, winH) = (size, size)

# loop over the image pyramid
# for resized in pyramid(image, scale=1.5):
# loop over the sliding window for each layer of the pyramid

for frame in test_frames:
    # print(frame)
    image = cv2.imread("./test_frames/" + str(frame))
    lower_red = np.array([150, 200, 150])
    upper_red = np.array([255, 255, 255])
    mask1 = cv2.inRange(image, lower_red, upper_red)
    # plt.imshow(mask1)
    # plt.show()
    image = np.asarray(mask1)
    for (x, y, window) in sliding_window(image, stepSize=size / 3, windowSize=(winW, winH)):
        # if the window does not meet our desired window size, ignore it
        if window.shape[0] == winH and window.shape[1] == winW:
            # continue
            # tutaj przetwarzamy okno
            window = window[np.newaxis, np.newaxis, :, :]
            clone = image.copy()
            cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 255, 0), 2)
            plt.imshow(clone)
            plt.ion()
            plt.show()
            # cv2.waitKey(1)
            # time.sleep(0.025)
            # classify the digit
            probs = model.predict(window)
            prediction = probs.argmax(axis=1)
            if int(prediction[0]) < 53:
                # resize the image from a 28 x 28 image to a 96 x 96 image so we
                # can better see it
                image = (window * 255).astype("uint8")
                image = cv2.merge([image] * 3)
                image = cv2.resize(image, (96, 96), interpolation=cv2.INTER_LINEAR)
                cv2.putText(image, str(prediction[0]), (5, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 150, 0), 2)

                # show the image and prediction
                print("[INFO] Predicted: {}".format(prediction[0]))
                cv2.imwrite("test_frames_results/" + frame + str(x) + str(y) + ".png", image)
                # cv2.waitKey(0)


# since we do not have a classifier, we'll just draw the window
#         clone = image.copy()
#         cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 255, 0), 2)
#         cv2.imshow("Window", clone)
#         cv2.waitKey(1)
#         time.sleep(0.025)
