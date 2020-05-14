import argparse
import sys
import enum
import random
from os import listdir
from os.path import isfile, join
import uuid
import os

from PIL import Image


try:
    from data_loaders.screenshot_loader import Datapoint
except ImportError:
    pass

try:
    # Trying to find module on sys.path
    from screenshot_loader import Datapoint
except ModuleNotFoundError:
    pass

try:
    from data_loaders import config
except ImportError:
    pass


class Data(Datapoint):

    __slot__ = [
        "path"
    ]

    CLASSES = [
        "close",
        "medium",
        "large",
        "others",
    ]

    MAPPER = {
        0: 0,
        1: 1,
        2: 2,
        9: 3,
    }

    def __init__(self,
                 path):
        super().__init__()
        self.path = path
        self._parse_path()
        if path.contains(self.CLASSES[0]):
            self.clas = self.CLASSES[0]
        elif path.contains(self.CLASSES[1]):
            self.clas = self.CLASSES[1]
        elif path.contains(self.CLASSES[2]):
            self.clas = self.CLASSES[2]
        elif path.contains(self.CLASSES[3]):
            self.clas = self.CLASSES[3]
        else:
            exit("There are no possible classes extracted")

    def download_image(self):
        self.image = Image.open(self.path)

    def _parse_path(self):
        path = self.path.replace("\"", "").replace("'", "")
        data = path("/")[-1]
        (year_director, self.title) = data.split("_-_")
        self.year = int(year_director[:4])
        self.director = year_director[4:]


class DownSampler(object):
    __slot__ = ["datapoints_director",
                "split_strategy",
                "dataset_size"]

    def __init__(self,
                 path,
                 split_strategy):
        self.split_strategy = split_strategy
        self.datapoints_director = {}
        self.dataset_size = 0

        print(path)
        for path, subdirs, files in os.walk(path):
            for name in files:
                print(os.path.join(path, name))

                datapoint = Data(os.path.join(path, name))
                if datapoint.director is None:
                    exit("Error while fetching the data")
                self.datapoints_director[datapoint.director] = datapoint
                self.dataset_size += 1

    def save(self):
        random_name = str(uuid.uuid1())

        training_size = round(self.dataset_size*0.8)
        validation_size = round(self.dataset_size*0.1)
        testing_size = (self.dataset_size - training_size) - training_size
        if self.split_strategy == SplitStrategy.RANDOM:
            datapoints = list(self.datapoints_director.values())
            random.shuffle(datapoints)
            training_set = datapoints[:training_size]
            validation_set = datapoints[training_size:validation_size+training_size]
            testing_set = datapoints[validation_size+training_size:]
        elif self.split_strategy == SplitStrategy.DIRECTOR:
            training_set = []
            validation_set = []
            testing_set = []
            for director in self.datapoints_director:
                if len(training_set) < training_size:
                    training_set.extend(self.datapoints_director[director])
                elif len(validation_set) < validation_size:
                    validation_set.extend(self.datapoints_director[director])
                else:
                    testing_set.extend(self.datapoints_director[director])
        else:
            exit("Not supported split strategy")
        try:
            os.mkdir("{0}_{1}".format(random_name,
                                      self.split_strategy))
        except FileExistsError:
            pass

        print(training_set, testing_set,
              validation_set, self.datapoints_director)
        self._save_set(
            training_set, "{0}_{1}/training".format(random_name,
                                                    self.split_strategy))
        self._save_set(testing_set,
                       "{0}_{1}/testing".format(random_name,
                                                self.split_strategy))
        self._save_set(validation_set, "{0}_{1}/validation".format(random_name,
                                                                   self.split_strategy))

    def _save_set(self,
                  dataset,
                  path):
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        for datapoint in dataset:
            datapoint.download_image()
            datapoint.image.save("{0}/{1}".format(path,
                                                  str(uuid.uuid1())))
            datapoint.purge()


class SplitStrategy(enum.Enum):
    NONE = 0
    RANDOM = 1
    DIRECTOR = 2
    MOVIE = 3


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pre-processs the dataset given a certain set of input to generate the actual layout for training, validating and testing')
    parser.add_argument('--load_from',
                        action="store",
                        default="",
                        dest="load_from",
                        help="")

    parser.add_argument('--no_split',
                        action="store_true",
                        default=True,
                        dest="no_split",
                        help='Does not split the dataset which lead to the generation of only one outcome directory')
    parser.add_argument('--split_random',
                        action="store_true",
                        default=False,
                        dest="split_random",
                        help='Split the dataset with a random approach')
    parser.add_argument('--split_director',
                        action="store_true",
                        default=False,
                        dest="split_director",
                        help='Split the dataset with a director based split of the dataset')

    args = parser.parse_args()

    picked_split = SplitStrategy.RANDOM
    if args.split_random:
        picked_split = SplitStrategy.RANDOM
    elif args.split_director:
        picked_split = SplitStrategy.DIRECTOR

    down_sampler = DownSampler(path=args.load_from,
                               split_strategy=picked_split)
    down_sampler.save()
