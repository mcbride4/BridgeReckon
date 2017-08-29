import os

import cv2
import numpy as np

from keras.optimizers import SGD
from keras.utils import np_utils
from sklearn.cross_validation import train_test_split

from src.kernel.cnn.networks.convolution_network_basis import Convolution_Network_Basis


class ModelPrep(object):
    def __init__(self, args):
        self.data = []
        self.args = args
        self.label = []
        self.card_names = []
        self.cards = []
        self.translate = {}
        self.data_preparation()

    def data_preparation(self):
        self.cards = os.listdir("./Cards/")
        i = 0
        i = self.load_cards_data(i)
        self.cards = os.listdir("./NoCards/")
        self.load_cards_data(i)
        f = open("translations.txt", 'w')
        f.write(repr(self.translate))
        f.close()
        self.data = np.asarray(self.data)

    def load_cards_data(self, i):
        for card in self.cards:
            card_name = card.replace(".png", "")
            self.card_names.append(card_name)
            files = os.listdir("./" + card_name)
            self.translate[i] = card_name
            for file in files:
                img = cv2.imread("./" + card_name + "/" + file)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.data.append(img)
                self.label.append(i)
            i += 1
        return i

    def model_compilation(self):
        print("[INFO] compiling model...")
        opt = SGD(lr=0.01)
        model = Convolution_Network_Basis.build(width=60, height=60, depth=1, classes=62,
                            weightsPath=self.args["weights"] if self.args["load_model"] > 0 else None)
        model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
        return model

    def save_model(self, model):
        print("[INFO] dumping weights to file...")
        model.save_weights(self.args["weights"], overwrite=True)

    def train_model(self, model):
        model.fit(self.train_data, self.train_labels, batch_size=128, nb_epoch=50,
                  verbose=1)

        print("[INFO] evaluating...")
        (loss, accuracy) = model.evaluate(self.test_data, self.test_labels,
                                          batch_size=128, verbose=1)
        print("[INFO] accuracy: {:.2f}%".format(accuracy * 100))

    def compile(self):
        data = self.data[:, np.newaxis, :, :]
        (self.train_data, self.test_data, self.train_labels, self.test_labels) = train_test_split(
            data / 255.0, self.label, test_size=0.1)
        self.train_labels = np_utils.to_categorical(self.train_labels, 62)
        self.test_labels = np_utils.to_categorical(self.test_labels, 62)
        return self.model_compilation()
