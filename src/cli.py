# USAGE
# python cli_deprecated.py --save-model 1 --weights output/lenet_weights.hdf5
# python cli_deprecated.py --load-model 1 --weights output/lenet_weights.hdf5

import argparse
import json
import os
import threading

import cv2
import numpy as np
import requests

from collections import Counter
from uuid import getnode as get_mac

from src.model_load import ModelPrep
from src.Inputs.slicing_window import sliding_window
from src.Inputs.VideoInputStreamWrapper import VideoInputStreamWrapper


class CameraThread(threading.Thread):
    def __init__(self, args=()):
        threading.Thread.__init__(self)
        self.daemon = True
        self.received_messages = args
        self.report = {}

    def run(self):
        print(threading.currentThread().getName(), self.received_messages)
        self.report['camera_id'] = self.received_messages
        input_camera = VideoInputStreamWrapper(int(self.report['camera_id'][-1]) - 1)
        img = input_camera.get_every_two_sec(120)
        for (x, y, window) in sliding_window(img, step_size=60 / 3,
                                             window_size=(60, 60)):

            if window.shape[0] == 60 and window.shape[1] == 60:
                window = window[np.newaxis, np.newaxis, :, :]
                clone = img.copy()
                cv2.rectangle(clone, (x, y), (x + 60, y + 60), (0, 255, 0), 2)
                if np.mean(window) > 0.1:
                    probs = self.model.predict(window)
        self.report['results'] = {"img": img, "cards": Counter(probs)}

    def get_report(self):
        return self.report


def send_report_to_receiver(reports):
    mac = get_mac()
    final_report = {'pi_id': mac}
    for report in reports:
        try:
            final_report[report['camera_id']] = report['results']
        except:
            pass
    final_report = json.dumps(final_report)
    r = requests.post('http://192.168.0.1', data=final_report)


class CliInterface:
    def __init__(self, argument_parser):
        argument_parser.add_argument("-s", "--save-model", type=int, default=-1,
                                     help="(optional) whether or not model should be saved to disk")
        argument_parser.add_argument("-l", "--load-model", type=int, default=-1,
                                     help="(optional) whether or not pre-trained model should be loaded")
        argument_parser.add_argument("-w", "--weights", type=str,
                                     help="(optional) path to weights file")
        self.args = vars(argument_parser.parse_args())
        self.model = ModelPrep(self.args).compile()
        cameras = ["id_1", "id_2"]
        threads = []
        while True:
            i = 0
            for camera in cameras:
                threads.append(CameraThread(args=camera))
                threads[i].start()
                i += 1
                reports = [thread.get_report() for thread in threads]
                send_report_to_receiver(reports)

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

            for (x, y, window) in sliding_window(image, step_size=windows_height / 3,
                                                      window_size=(windows_width, windows_height)):

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
