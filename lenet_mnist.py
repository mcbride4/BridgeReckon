# USAGE
# python lenet_mnist.py --save-model 1 --weights output/lenet_weights.hdf5
# python lenet_mnist.py --load-model 1 --weights output/lenet_weights.hdf5

# import the necessary packages
from pyimagesearch.cnn.networks import LeNet
from sklearn.cross_validation import train_test_split
from sklearn import datasets
from keras.optimizers import SGD
from keras.utils import np_utils
import numpy as np
import argparse
import os
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--save-model", type=int, default=-1,
                help="(optional) whether or not model should be saved to disk")
ap.add_argument("-l", "--load-model", type=int, default=-1,
                help="(optional) whether or not pre-trained model should be loaded")
ap.add_argument("-w", "--weights", type=str,
                help="(optional) path to weights file")
args = vars(ap.parse_args())

# grab the MNIST dataset (if this is your first time running this
# script, the download may take a minute -- the 55MB MNIST dataset
# will be downloaded)
# print("[INFO] downloading MNIST...")
# dataset = datasets.fetch_mldata("MNIST Original")
# print((dataset.data.shape))
cards = os.listdir("./Cards/")
label = []
data = []
card_names = []
translate = {}
i = 0
for card in cards:
    card_name = card.replace(".png", "")
    card_names.append(card_name)
    files = os.listdir("./" + card_name)
    translate[i] = card_name
    for file in files:
        img = cv2.imread("./" + card_name + "/" + file)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # print(repr(img.shape), card_name)
        data.append(img)
        label.append(i)
    i += 1
cards = os.listdir("./NoCards/")
for card in cards:
    card_name = card.replace(".png", "")
    card_names.append(card_name)
    files = os.listdir("./" + card_name)
    translate[i] = card_name
    for file in files:
        img = cv2.imread("./" + card_name + "/" + file)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # print(repr(img.shape), card_name)
        data.append(img)
        label.append(i)
    i += 1
f = open("translateion.txt", 'w')
f.write(repr(translate))
f.close()
# print(type(data[1]))
data = np.asarray(data)
print(repr(data.shape))
dataset = datasets.base.Bunch(label=label, data=(data))
# # reshape the MNIST dataset from a flat list of 784-dim vectors, to
# # 28 x 28 pixel images, then scale the data to the range [0, 1.0]
# # and construct the training and testing splits
data = data[:, np.newaxis, :, :]
(trainData, testData, trainLabels, testLabels) = train_test_split(
    data / 255.0, label, test_size=0.1)
#
# # transform the training and testing labels into vectors in the
# # range [0, classes] -- this generates a vector for each label,
# # where the index of the label is set to `1` and all other entries
# # to `0`; in the case of MNIST, there are 10 class labels
trainLabels = np_utils.to_categorical(trainLabels, 62)
testLabels = np_utils.to_categorical(testLabels, 62)
#
# # initialize the optimizer and model
print("[INFO] compiling model...")
opt = SGD(lr=0.01)
model = LeNet.build(width=60, height=60, depth=1, classes=62,
                    weightsPath=args["weights"] if args["load_model"] > 0 else None)
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
#
# # only train and evaluate the model if we *are not* loading a
# # pre-existing model
if args["load_model"] < 0:
    print("[INFO] training...")
    model.fit(trainData, trainLabels, batch_size=128, nb_epoch=50,
              verbose=1)

    # show the accuracy on the testing set
    print("[INFO] evaluating...")
    (loss, accuracy) = model.evaluate(testData, testLabels,
                                      batch_size=128, verbose=1)
    print("[INFO] accuracy: {:.2f}%".format(accuracy * 100))

# check to see if the model should be saved to file
if args["save_model"] > 0:
    print("[INFO] dumping weights to file...")
    model.save_weights(args["weights"], overwrite=True)

# randomly select a few testing digits
for i in np.random.choice(np.arange(0, len(testLabels)), size=(10,)):
    # classify the digit
    probs = model.predict(testData[np.newaxis, i])
    prediction = probs.argmax(axis=1)

    # resize the image from a 28 x 28 image to a 96 x 96 image so we
    # can better see it
    image = (testData[i][0] * 255).astype("uint8")
    image = cv2.merge([image] * 3)
    image = cv2.resize(image, (96, 96), interpolation=cv2.INTER_LINEAR)
    cv2.putText(image, str(prediction[0]), (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # show the image and prediction
    print("[INFO] Predicted: {}, Actual: {}".format(prediction[0],
                                                    np.argmax(testLabels[i])))
    cv2.imwrite("Digit" + str(i) + ".png", image)
# cv2.waitKey(0)
