import boto3
import tempfile
import argparse
import csv
import unidecode
import sys
import enum
import random
from datetime import datetime
import os
from zipfile import ZipFile

from PIL import Image


try:
    from data_loaders import config
except ImportError:
    pass

try:
    # Trying to find module on sys.path
    import configs
except ModuleNotFoundError:
    pass

s3 = boto3.resource('s3', region_name=configs.S3_REGION_NAME)


class Datapoint(object):

    __slot__ = [
        "uuid",
        "id",
        "year",
        "director",
        "title",
        "timestamp",
        "clas",
        "image",
        "image_path"
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
                 id=None,
                 year=None,
                 director=None,
                 title=None,
                 timestamp=None,
                 clas=None,
                 image_path=None):
        super().__init__()
        self.id = id
        # self.s3_client = boto3.resource('s3')
        self.year = int(year) if year is not None else None
        self.director = director
        self.title = title
        self.timestamp = timestamp
        self.clas = int(float(clas))
        self.image_path = image_path
        self.order = int(id) if id is not None else None
        self.uuid = "{0}_{1}_{2}_{3}".format(director, year, title, id)
        self.image = None

    def download_image(self):
        if self.id is None or self.year is None or self.director is None or self.title is None:
            raise RuntimeError(
                "Can't load image - There is at least one none value - ID : {0}, Year: {1}, Director: {2}, Title: {3}".format(self.id, self.year, self.director, self.title))

        bucket = s3.Bucket(configs.S3_INPUT_BUCKET_NAME)
        fail = 0
        path = u"{0}/{1}".format(
            u"{0}_{1}".format(self.year,
                              self.build_key()),
            u"{0}.jpg".format(str(self.id).zfill(5)))
        while self.image_path is None and fail < 2:
            try:
                obj = bucket.Object(path)
                tmp = tempfile.NamedTemporaryFile()

                with open(tmp.name, 'wb') as f:
                    obj.download_fileobj(f)

                self.image_path = tmp
            except:
                fail += 1
                if self.image_path is None:
                    print(path, sys.exc_info()[0])
        return True

    def build_key(self):
        return unidecode.unidecode("{0}_-_{1}".format(self.director.replace(" ", "_"),
                                                      self.title.replace(" ", "_").replace("'", "_")))

    def obtain_classname(self):
        return self.CLASSES[self.MAPPER[self.clas]]


class ShotScaleLoader(object):
    __slot__ = ["s3_client",
                "datapoints",
                "classes_datapoints"]

    def __init__(self):
        super().__init__()
        self.s3_client = boto3.resource('s3')
        self.datapoints = []

    def obtain_datapoints(self):
        self._load_classes_datapoints()

        movies_linked = 0
        for directory in self._load_directories():
            year = directory[: 4]
            key = directory[5:]
            if key in self.classes_datapoints:
                movies_linked += 1
                for datapoint in self.classes_datapoints[key]:
                    datapoint.year = int(year)
                    self.datapoints.append(datapoint)

        print("Total number of movies : {0}".format(
            movies_linked))
        print("Total datapoints : {0}".format(
            len(self.datapoints)))

    def _load_directories(self):
        print("{0} Movies loaded".format(
            len(configs.S3_INPUT_DIRECTORIES_NAMES)))
        return configs.S3_INPUT_DIRECTORIES_NAMES

    def _load_classes_datapoints(self,
                                 class_path=configs.LOCAL_INPUT_CLASSES):
        classes_datapoints = {}

        loading = 0
        with open(class_path) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                datapoint = Datapoint(id=int(row[configs.LOCAL_INPUT_HEADER_ID])+1,
                                      director=row[configs.LOCAL_INPUT_HEADER_DIRECTOR],
                                      title=row[configs.LOCAL_INPUT_HEADER_TITLE],
                                      timestamp=self._timestamp_to_second(
                                          row[configs.LOCAL_INPUT_HEADER_TIMESTAMP]),
                                      clas=row[configs.LOCAL_INPUT_HEADER_CLASS])
                key = datapoint.build_key()
                if key not in classes_datapoints:
                    classes_datapoints[key] = []
                classes_datapoints[key].append(datapoint)
                if loading % 100000 == 0:
                    print("{0} Datapoint(s) loaded".format(loading))
                loading += 1

        self.classes_datapoints = classes_datapoints

    def _timestamp_to_second(self,
                             timestamp):
        (hours, minutes, seconds) = timestamp.split(":")

        return int(hours)*3600 + int(minutes)*60 + int(seconds)


class ResizeAlgorithm(enum.Enum):
    UNKNOWN = 0
    CROPPED = 1
    RESCALE = 2


class SplitStrategy(enum.Enum):
    RANDOM = 0
    DIRECTOR = 1
    MOVIE = 2


class ShotScaleExporter(object):

    def __init__(self,
                 datapoints,
                 algorithm=ResizeAlgorithm.UNKNOWN,
                 split_strategy=SplitStrategy.RANDOM):
        super().__init__()
        self.datapoints = datapoints
        self.algorithm = algorithm
        self.split_strategy = split_strategy

    def mix(self):
        if self.split_strategy == SplitStrategy.RANDOM:
            random.shuffle(self.datapoints)
        else:
            exit("{0} Split strategy is not supported".format(self.split_strategy))

    def save(self):
        skipped_images = 0
        for datapoint in self.datapoints:
            datapoint.download_image()
            if datapoint.image_path is not None:
                datapoint.image = self._transform_image(datapoint.image_path)
                self._save(datapoint)
            else:
                skipped_images += 1
        self._compress()
        print("{0} images skipped over {1} initial images so {2} images saved".format(skipped_images,
                                                                                      len(
                                                                                          self.datapoints),
                                                                                      len(self.datapoints)-skipped_images))

    def _save(self,
              datapoint):
        exit("No implementation for this save")

    def _compress(self):
        exit("No implementation for this compress")

    def _transform_image(self,
                         image_path):
        image = Image.open(image_path)

        if self.algorithm == ResizeAlgorithm.CROPPED:
            lowest = min(image.width, image.height)
            ratio = lowest / configs.OUTPUT_IMAGE_SIZE
            size = [round(image.width/ratio), round(image.height/ratio)]
            image = image.resize(size,
                                 resample=Image.BICUBIC)
            left = (image.width - configs.OUTPUT_IMAGE_SIZE)/2
            top = (image.height - configs.OUTPUT_IMAGE_SIZE)/2
            right = (image.width + configs.OUTPUT_IMAGE_SIZE)/2
            bottom = (image.height + configs.OUTPUT_IMAGE_SIZE)/2
            image = image.crop((left, top, right, bottom))
        elif self.algorithm == ResizeAlgorithm.RESCALE:
            image = image.resize([configs.OUTPUT_IMAGE_SIZE, configs.OUTPUT_IMAGE_SIZE],
                                 resample=Image.BICUBIC)
        else:
            exit("The Resize {0} Algorithm is not supported".format(
                self.algorithm))

        return image


class ShotScaleLocalExporter(ShotScaleExporter):
    __slots__ = [
        "path",
        "tmp",
    ]

    def __init__(self,
                 path,
                 datapoints,
                 tmp=configs.DEFAULT_OUTPUT_NAME,
                 algorithm=ResizeAlgorithm.UNKNOWN,
                 split_strategy=SplitStrategy.RANDOM):
        super().__init__(datapoints, algorithm=algorithm, split_strategy=split_strategy)
        self.path = path
        self.tmp = "{0}__{1}".format(
            tmp, datetime.now().strftime("%d-%m-%Y_%H:%M:%S"))

    def _save(self,
              datapoint):
        path = "{0}{1}/".format(self.path,
                                self.tmp)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        path = "{0}{1}".format(path,
                               datapoint.obtain_classname())
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        filename = "{0}.{1}.{2}".format(
            datapoint.uuid,
            self.algorithm,
            "jpg")
        datapoint.image.save("{0}/{1}".format(path,
                                              filename))
        datapoint.image = None

    def _compress(self):
        with ZipFile("{0}{1}{2}".format(self.path,
                                        self.tmp,
                                        ".zip"), 'w') as zipObj:
            for folderName, _, filenames in os.walk("{0}{1}{2}".format(self.path,
                                                                       self.tmp,
                                                                       "/")):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pre-processs the dataset given a certain set of input to generate the actual layout for training, validating and testing')
    parser.add_argument('--local_save',
                        action="store",
                        default="",
                        dest="local_save",
                        help="")
    parser.add_argument('--remote_save',
                        action="store_true",
                        default=False,
                        dest="remote_save",
                        help="")
    parser.add_argument('--rescale',
                        action="store_true",
                        default=False,
                        dest="rescale_resize",
                        help='Simply resize rescale the images')
    parser.add_argument('--cropped',
                        action="store_true",
                        default=False,
                        dest="cropped_resize",
                        help='Crop the image to fit the tageted size')

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
    parser.add_argument('--split_movie',
                        action="store_true",
                        default=False,
                        dest="split_movie",
                        help='Split the dataset with a movie based split of the dataset')

    parser.add_argument('--size',
                        action="store",
                        dest="size",
                        default=1000000,
                        type=int,
                        help="Size of the dataset, by default all the dataset will be used, for local use you may want to lower the size of the dataset (size 1000 for example)")

    args = parser.parse_args()

    picked_algo = ResizeAlgorithm.UNKNOWN
    if args.cropped_resize:
        picked_algo = ResizeAlgorithm.CROPPED
    elif args.rescale_resize:
        picked_algo = ResizeAlgorithm.RESCALE
    else:
        exit("Error - You must pick an algorithm see --help !")

    picked_split = SplitStrategy.RANDOM
    if args.split_random:
        picked_split = SplitStrategy.RANDOM
    elif args.split_director:
        picked_split = SplitStrategy.DIRECTOR
    elif args.split_movie:
        picked_split = SplitStrategy.MOVIE

    if args.local_save != "" and not args.remote_save:
        shotscale_loader = ShotScaleLoader()
        shotscale_loader.obtain_datapoints()
        shotscale_exporter = ShotScaleLocalExporter(datapoints=shotscale_loader.datapoints,
                                                    path=args.local_save,
                                                    algorithm=picked_algo,
                                                    split_strategy=picked_split)
        shotscale_exporter.save()
        # shotscale_loader.local_save(dest=args.local_save,
        #                             size=size)
    if args.remote_save and args.local_save == "":
        shotscale_loader = ShotScaleLoader()
        shotscale_loader.obtain_datapoints()
        # shotscale_exporter = ShotScaleExporter(shotscale_loader.datapoints,
        #                                        algorithm=picked_algo,
        #                                        split=picked_split)
        # shotscale_exporter.mix()
        # shotscale_exporter.save()

        # shotscale_loader.remote_save(size=size)

    exit("Error - You must setup a local path or send it to remote !")
