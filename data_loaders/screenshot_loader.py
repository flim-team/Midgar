import boto3
import tempfile

import csv


s3 = boto3.resource('s3', region_name='eu-central-1')


class Datapoint(object):
    S3_BUCKET_NAME = u"flim-ai-sagemaker"

    __slot__ = [
        "s3_client",
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
        "medium"
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
        self.clas = clas
        self.image_path = image_path
        self.order = int(id) if id is not None else None

    def load_image(self):
        if self.id is None or self.year is None or self.director is None or self.title is None:
            raise RuntimeError(
                "Can't load image - There is at least one none value - ID : {0}, Year: {1}, Director: {2}, Title: {3}".format(self.id, self.year, self.director, self.title))

        bucket = s3.Bucket(self.S3_BUCKET_NAME)
        obj = bucket.Object("{0}/{1}".format(
            "{0}_{1}_-_{2}".format(self.year,
                                   self.director.replace(" ",
                                                         "_"),
                                   self.title.replace(" ", "_")),
            "{0}.jpg".format(str(self.id).zfill(5))))

        tmp = tempfile.NamedTemporaryFile()

        with open(tmp.name, 'wb') as f:
            obj.download_fileobj(f)

        self.image_path = tmp


class ShotScaleLoader(object):
    __slot__ = ["s3_client",
                "datapoints",
                "classes_datapoints"]

    HEADER_ID = "ID"
    HEADER_TITLE = "movie"
    HEADER_DIRECTOR = "author"
    HEADER_CLASS = "Class"
    HEADER_TIMESTAMP = "movietime"

    S3_BUCKET_NAME = u"flim-ai-sagemaker"

    CLASSES_PATH = u"data/dataset_movie.csv"

    def __init__(self):
        super().__init__()
        self.s3_client = boto3.resource('s3')
        self.datapoints = []

    def obtain_datapoints(self):
        self._load_classes_datapoints()

        for directory in self._load_directories():
            year = directory["key"][: 4]
            key = directory["key"][5:]
            if key in self.classes_datapoints:
                for datapoint in self.classes_datapoints[key]:
                    datapoint.year = int(year)
                    self.datapoints.append(datapoint)

        print(
            "Total datapoints : {0}".format(len(self.datapoints)))

    def _load_directories(self,
                          bucket=S3_BUCKET_NAME):
        directories = []
        for file in self.s3_client.Bucket(
                bucket).objects.filter(Delimiter='/'):
            if file.key[-4:] == ".mp4":
                directories.append({
                    "bucket_name": file.bucket_name,
                    "key": file.key[:-4]
                })
        return directories

    def _load_classes_datapoints(self,
                                 class_path=CLASSES_PATH):
        classes_datapoints = {}

        loading = 0
        with open(class_path) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                key = self._build_key(title=row[self.HEADER_TITLE],
                                      director=row[self.HEADER_DIRECTOR])
                datapoint = Datapoint(id=int(row[self.HEADER_ID])+1,
                                      director=row[self.HEADER_DIRECTOR],
                                      title=row[self.HEADER_TITLE],
                                      timestamp=self._timestamp_to_second(row[self.HEADER_TIMESTAMP]))
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

    def _build_key(self,
                   title,
                   director):
        return "{0}_-_{1}".format(director.replace(" ", "_"),
                                  title.replace(" ", "_"))


if __name__ == '__main__':
    ShotScaleLoader().obtain_datapoints()
