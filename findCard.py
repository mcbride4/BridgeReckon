import PIL
import matplotlib.pyplot as plt
import numpy as np
import cv2


def create_sample_set(mask, N=12, shape_color=[0, 0, 1., 1.]):
    rv = np.ones((N, mask.shape[0], mask.shape[1], 4), dtype=np.float)
    mask = mask.astype(bool)
    for i in range(N):
        for j in range(3):
            current_color_layer = rv[i, :, :, j]
            current_color_layer[:, :] *= np.random.random()
            current_color_layer[mask] = np.ones((mask.sum())) * shape_color[j]
    return rv

img2 = cv2.imread("/home/ubuntu/Desktop/karty2.png")
lower_red = np.array([150,200,150])
upper_red = np.array([255,255,255])
mask1 = cv2.inRange(img2, lower_red, upper_red)
cv2.imwrite("mask.png", mask1)
# plt.imshow(mask1)
# plt.show()
# mask = mask1
# output_img = img2.copy()
# output_img[np.where(mask==0)] = 0
# kernel = np.ones((5,5),np.float32)/15
# output_img = cv2.filter2D(output_img,-1,kernel)
# img = output_img[:,:,0].astype('uint8')
#
# kernel = np.ones((3,3),np.uint8)
# opening = cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel, iterations = 2)
#
# _, contours, _ = cv2.findContours(opening,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_TC89_L1)
# images = []
# for cnt in contours:
#     x,y,w,h = cv2.boundingRect(cnt)
#     if (100 < w < 300) and (150 < h < 300):
#         print(w/h)
#         cv2.rectangle(img,(x,y),(x+w,y+h),(110,110,110),2)
#         images.append(img[y:(y+h), x:(x+w)])
#
# plt.imshow(img)
# plt.gray()
# plt.show()
# print(len(images))
# for card in range(0, len(images)):
#     plt.subplot(2, int((len(images) + 1) / 2), card+1)
#     plt.imshow(images[card])

# plt.show()
