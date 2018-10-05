import numpy as np
from skimage.transform import resize


def sliding_window(image, step_size, window_size):
    # slide a window across the image
    cards = []
    for y in range(0, image.shape[0] - window_size[0], int(step_size)):
        for x in range(0, image.shape[1] - window_size[0], int(step_size)):
            # yield the current window
            wind = image[y:y + window_size[1], x:x + window_size[0]].astype(float)
            if 0.94 > np.mean(wind) > 0.5:
                card = resize(wind, (224, 224))
                card_3 = np.asarray([card, card, card])
                cards.append(card_3)
    return cards
