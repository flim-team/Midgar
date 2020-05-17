import os
from PIL import Image as pil_image
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy

class DataAugementation():
    # Read Img from a folder
    def ReadImg(self, file):
        filelist = os.listdir(file)
        data = []
        label = []

        for img in filelist:
            original = pil_image.open(file+'/'+img)
            data.append(original)
            label.append(file.split('/')[-1])

        return data, label

    def convert(self, image, label): # convert img to tensor
        outputimg = []
        outputlabel = []

        for i in range(len(image)):
            outimage = tf.image.convert_image_dtype(image[i], tf.float32) # Cast and normalize to image to [0,1]
            outputimg.append(outimage)
            outputlabel.append(label[i])

        return outputimg, outputlabel

    def augement(self, image, label): # image and lable list
        image, label = self.convert(image, label)
        outputimg = []
        outputlabel = []
        size = image[0].shape

        for i in range(len(image)):
            image_1 = tf.image.flip_left_right(image[i]) # Flip
            image_pad = tf.image.resize_with_crop_or_pad(image[i], 298, 362) # Add 10 pixels of padding, No operand here
            image_2 = tf.image.random_crop(image_pad, size = size) # Random crop back 
            image_3 = tf.image.random_brightness(image[i], max_delta=0.5) # Random brightness
            noise = tf.random.normal(shape=tf.shape(image[i]), mean=0.0, stddev=1.0, dtype=tf.float32)
            image_4 = tf.add(image[i], noise) # Gaussian noise
            outputimg.extend([image_1,image_2, image_3,image_4])
            outputlabel.extend([label[i]]*4)
        return outputimg, outputlabel

    def __run__(self):
        augement = True # enable data augementation
        filename = './data/test_augmentation'
        [data, label] = self.ReadImg(filename)

        if (augement):
            [data, label] = self.augement(data, label)
            print("output:",data)
            print("label:",label)

        else:
            [data, label] = da.convert(data[0],label)


da = DataAugementation()
da.__run__()