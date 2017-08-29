from src.Inputs.slicing_window import sliding_window
import numpy as np

import unittest


class TestSlidingWindow(unittest.TestCase):

    def test_sliding_window(self):
        img = np.zeros((200, 200))
        img[100:120, 100:120] = 1
        i = 0
        for (x, y, window) in sliding_window(img, step_size=60 / 3, window_size=(60, 60)):
            i += 1
        self.assertEqual(i, 9)


if __name__ == '__main__':
    unittest.main()
