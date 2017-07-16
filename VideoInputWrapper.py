import skvideo.io


class VideoInputWrapper(object):
    def __init__(self, device=0):
        self.device = device
        self.vidcap = skvideo.io.vreader(self.device, as_grey=True)

    def return_every_n_frame(self, n):
        # TODO
        pass
