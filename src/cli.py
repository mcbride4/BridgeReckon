# USAGE
# python cli_deprecated.py --save-model 1 --weights output/lenet_weights.hdf5
# python cli_deprecated.py --load-model 1 --weights output/lenet_weights.hdf5

import argparse
import os

import cv2
import numpy as np

from src.model_load import ModelPrep


class CliInterface():
    def __init__(self, argument_parser):
        argument_parser.add_argument("-s", "--save-model", type=int, default=-1,
                                     help="(optional) whether or not model should be saved to disk")
        argument_parser.add_argument("-l", "--load-model", type=int, default=-1,
                                     help="(optional) whether or not pre-trained model should be loaded")
        argument_parser.add_argument("-w", "--weights", type=str,
                                     help="(optional) path to weights file")
        self.args = vars(argument_parser.parse_args())
        self.model = ModelPrep(self.args).compile()
        self.predict_test_data()

    def sliding_window(image, stepSize, windowSize):
        # slide a window across the image
        for y in range(0, image.shape[0], int(stepSize)):
            for x in range(0, image.shape[1], int(stepSize)):
                # yield the current window
                yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

    @staticmethod
    def load_test_frames():
        test_frames = os.listdir("./test_frames")
        size = 60
        (winW, winH) = (size, size)
        return test_frames, winH, winW

    def predict_test_data(self):
        (test_frames, windows_height, windows_width) = self.load_test_frames()
        for frame in test_frames:
            image = cv2.imread("./test_frames/" + str(frame))
            lower_red = np.array([150, 200, 150])
            upper_red = np.array([255, 255, 255])
            mask1 = cv2.inRange(image, lower_red, upper_red)
            image = np.asarray(mask1)

            for (x, y, window) in self.sliding_window(image, stepSize=windows_height / 3,
                                                      windowSize=(windows_width, windows_height)):

                if window.shape[0] == windows_height and window.shape[1] == windows_width:
                    window = window[np.newaxis, np.newaxis, :, :]
                    clone = image.copy()
                    cv2.rectangle(clone, (x, y), (x + windows_width, y + windows_height), (0, 255, 0), 2)
                    probs = self.model.predict(window)
                    prediction = probs.argmax(axis=1)

                    if int(prediction[0]) < 53:
                        image = (window * 255).astype("uint8")
                        image = cv2.merge([image] * 3)
                        image = cv2.resize(image, (96, 96), interpolation=cv2.INTER_LINEAR)
                        cv2.putText(image, str(prediction[0]), (5, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 150, 0), 2)

                        print("[INFO] Predicted: {}".format(prediction[0]))
                        cv2.imwrite("test_frames_results/" + frame + str(x) + str(y) + ".png", image)

cli = CliInterface(argparse.ArgumentParser())
