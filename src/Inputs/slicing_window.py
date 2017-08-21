import numpy as np


def sliding_window(image, step_size, window_size):
    # slide a window across the image
    for y in range(0, image.shape[0], int(step_size)):
        for x in range(0, image.shape[1], int(step_size)):
            # yield the current window
            if np.mean(image[y:y + window_size[1], x:x + window_size[0]], axis=None) > 0.01:
                yield (x, y, image[y:y + window_size[1], x:x + window_size[0]])