import json
import numpy as np
import torch
from torchvision.models import alexnet
from slicing_window import sliding_window
import requests
from torch.utils.data import DataLoader, Dataset
import sys
from glob import glob
import os
from skimage import io


class WindDataset(Dataset):
    def __init__(self, winds):
        self.windows = winds

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, index):
        return self.windows[index]


class Pred:
    def __init__(self, model, data):
        self.data = data
        self.val_to_card = {0: 'AS', 1: '3D', 2: '4D', 3: '5C', 4: '6H', 5: 'QC', 6: 'JS', 7: 'KH', 8: 'KC', 9: 'TH',
                            10: '3C', 11: '2D', 12: 'AC', 13: 'JC', 14: '2C', 15: '4H', 16: '9S', 17: 'AH', 18: '7D',
                            19: '6C', 20: 'KD', 21: '4C', 22: 'TD', 23: 'AD', 24: '5H', 25: '6S', 26: '9D', 27: '3H',
                            28: '7S', 29: 'TS', 30: '2H', 31: 'QH', 32: 'QD', 33: '6D', 34: 'KS', 35: 'JD', 36: '8D',
                            37: '9H', 38: '3S', 39: '5D', 40: 'TC', 41: '2S', 42: '7H', 43: 'JH', 44: '8S', 45: '5S',
                            46: '9C', 47: '7C', 48: '4S', 49: '8H', 50: '8C', 51: 'QS', 52: 'no10', 53: 'no1',
                            54: 'no3', 55: 'no9', 56: 'no8', 57: 'no2', 58: 'no5', 59: 'no4', 60: 'no6', 61: 'no7'}
        self.card_to_val = {}
        self.model = model
        return

    def run(self):

            results = {}
            for key in self.data.keys():

                if 'camera' in key:
                    image = np.asarray(self.data['img']) / 2 ** 16
                    possible_cards = sliding_window(image, step_size=20, window_size=(60, 60))
                    results['camera_id'] = int(self.data[key])
                    if len(possible_cards) == 0:
                        results['cards'] = [52, ]
                        results['raspberry_id'] = 1
                    else:
                        results['cards'] = []
                        results['raspberry_id'] = 1
                        dataset = WindDataset(possible_cards)
                        dl = DataLoader(dataset, batch_size=64)
                        all_pred = []
                        for i, data in enumerate(dl):
                            inputs = (data - 0.7829) / 0.370
                            self.model.eval()
                            labels = self.model(inputs.float())
                            _, pred = torch.max(labels, 1)
                            pred = pred.numpy()
                            all_pred.extend(pred.tolist())
                        uniq, counts = np.unique(all_pred, return_counts=True)
                        cards = []
                        for j in range(len(uniq)):
                            if uniq[j] < 52:
                                cards.append([self.val_to_card[uniq[j]], int(counts[j])])
                        results['cards'].extend(cards)
                        results['path'] = self.data['path']
                        # results['img'] = image.tolist()
                        r = json.dumps(results)
                        print(results['cards'])

                        requests.post('http://127.0.0.1:5000/snapshots', r)
                        print(r)
                        results = {}


def prepare_data(file):
    pi_id = file.split('/')[-3]
    cam_id = file.split('/')[-2]
    a = True
    while a:
        try:
            img = io.imread(file)
            a = False
        except Exception as e:
            pass
    data = {
        'raspberry_id': int(pi_id),
        'camera_id': int(cam_id[-1]),
        'img': img,
        'path': file,
    }
    return data


def main():
    # dir_read = sys.argv[0]

    with torch.no_grad():
        already_done = []
        model = alexnet(False)
        model.load_state_dict(torch.load('/home/dawid_rymarczyk/Pobrane/alexnet_model_longer.pth', map_location='cpu'))
        while True:
            files = glob('/home/dawid_rymarczyk/Pobrane/BridgeReckon-user_interface/src/flask/app/static/1/*/*.png')
            files.sort(key=os.path.getmtime)
            for file in files:
                if file in already_done:
                    pass
                else:
                    data = prepare_data(file)
                    p = Pred(model, data)
                    p.run()
                    already_done.append(file)


if __name__ == '__main__':
    main()
