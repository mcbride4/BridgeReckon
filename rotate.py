import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

cards = os.listdir("./NoCards/")
cards_name = []
for card in cards:
    img = cv2.imread("NoCards/" + card)
    lower_red = np.array([150, 200, 150])
    upper_red = np.array([255, 255, 255])
    mask1 = cv2.inRange(img, lower_red, upper_red)
    img = Image.fromarray(mask1)
    try:
        os.mkdir(card.replace(".png", ''))
    except:
        pass
    for i in range(1, 360):
        img_n = img.rotate(i, 0)
        img_n.save("./" + card .replace(".png", "") + "/" + str(i) + ".png")

#
# plt.imshow(mask1)
# plt.show()