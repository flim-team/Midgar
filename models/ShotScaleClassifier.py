import time

import tensorflow as tf
import tensorflow_hub as hub

from tensorflow.keras import layers

import numpy as np
import PIL.Image as Image
import matplotlib.pylab as plt

MOBILENETV2 = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4"
MOBILENETV2CLASSIFIER = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
INCEPTIONV3 = "https://tfhub.dev/google/tf2-preview/inception_v3/feature_vector/4"


class ShotScaleClassifier:
    __slots__ = ("name", "image_shape", "base_model",
                 "number_classes", "model",
                 "labels_path", "image_net_labels")

    def __init__(self, name="mobile_net", test=True, number_classes=5):
        if name == "mobile_net":
            self.image_shape = (224, 224, 3)
            if test:
                # load model from hub for immediate prediction
                self.model = tf.keras.Sequential([
                    hub.KerasLayer(MOBILENETV2CLASSIFIER,
                                   input_shape=self.image_shape)
                ])
                self.labels_path = tf.keras.utils.get_file('ImageNetLabels.txt',
                                                           'https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt')
                self.image_net_labels = np.array(open(self.labels_path).read().splitlines())
            else:
                self.base_model = hub.KerasLayer(MOBILENETV2,
                                                 input_shape=self.image_shape)
                self.number_classes = number_classes
                self.model = tf.keras.Sequential([
                    self.base_model,
                    layers.Dense(self.number_classes)
                ])

                self.base_model.trainable = False
                self.model.compile(optimizer=tf.keras.optimizers.Adam(),
                                   loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                                   metrics=['acc'])
        elif name == "inception":
            self.image_shape = (299, 299, 3)
            self.base_model = hub.KerasLayer(INCEPTIONV3,
                                             input_shape=self.image_shape)
            self.number_classes = number_classes
            self.model = tf.keras.Sequential([
                self.base_model,
                layers.Dense(self.number_classes)
            ])

            self.base_model.trainable = False
            self.model.compile(optimizer=tf.keras.optimizers.Adam(),
                               loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                               metrics=['acc'])

    def summary(self):
        self.model.summary()

    def test(self):
        # load an image
        grace_hopper = tf.keras.utils.get_file('image.jpg',
                                               'https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg')
        grace_hopper = Image.open(grace_hopper).resize((224, 224))
        # preprocess
        grace_hopper = np.array(grace_hopper) / 255.0
        # inference
        result = self.model.predict(grace_hopper[np.newaxis, ...])
        # result
        predicted_class = np.argmax(result[0], axis=-1)
        print(predicted_class)
        # show result
        plt.imshow(grace_hopper)
        plt.axis('off')
        predicted_class_name = self.image_net_labels[predicted_class]
        _ = plt.title("Prediction: " + predicted_class_name.title())
        plt.show()

    def test_batch(self):
        # load dataset
        data_root = tf.keras.utils.get_file(
            'flower_photos', 'https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz',
            untar=True)
        # transform in generator of batch
        image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1 / 255)
        image_data = image_generator.flow_from_directory(str(data_root), target_size=(224, 224))

        for image_batch, label_batch in image_data:
            # inference
            result_batch = self.model.predict(image_batch)
            # results
            predicted_class_names = self.image_net_labels[np.argmax(result_batch, axis=-1)]
            # show results
            plt.figure(figsize=(10, 9))
            plt.subplots_adjust(hspace=0.5)
            for n in range(30):
                plt.subplot(6, 5, n + 1)
                plt.imshow(image_batch[n])
                plt.title(predicted_class_names[n])
                plt.axis('off')
            _ = plt.suptitle("ImageNet predictions")
            plt.show()
            break
        model.summary()

    def test_batch_features(self):
        # load dataset
        data_root = tf.keras.utils.get_file(
            'flower_photos', 'https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz',
            untar=True)
        # transform in generator of batch
        image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1 / 255)
        image_data = image_generator.flow_from_directory(str(data_root), target_size=(self.image_shape[0],
                                                                                      self.image_shape[1]))

        steps_per_epoch = np.ceil(image_data.samples / image_data.batch_size)

        batch_stats_callback = CollectBatchStats()

        history = self.model.fit_generator(image_data, epochs=2,
                                           steps_per_epoch=steps_per_epoch,
                                           callbacks=[batch_stats_callback])

        plt.figure()
        plt.ylabel("Loss")
        plt.xlabel("Training Steps")
        plt.ylim([0, 2])
        plt.plot(batch_stats_callback.batch_losses)
        plt.show()

        plt.figure()
        plt.ylabel("Accuracy")
        plt.xlabel("Training Steps")
        plt.ylim([0, 1])
        plt.plot(batch_stats_callback.batch_acc)
        plt.show()

        class_names = sorted(image_data.class_indices.items(), key=lambda pair: pair[1])
        class_names = np.array([key.title() for key, value in class_names])

        for image_batch, label_batch in image_data:
            predicted_batch = self.model.predict(image_batch)
            predicted_id = np.argmax(predicted_batch, axis=-1)
            predicted_label_batch = class_names[predicted_id]
            label_id = np.argmax(label_batch, axis=-1)
            plt.figure(figsize=(10, 9))
            plt.subplots_adjust(hspace=0.5)
            for n in range(30):
                plt.subplot(6, 5, n + 1)
                plt.imshow(image_batch[n])
                color = "green" if predicted_id[n] == label_id[n] else "red"
                plt.title(predicted_label_batch[n].title(), color=color)
                plt.axis('off')
            _ = plt.suptitle("Model predictions (green: correct, red: incorrect)")
            plt.show()
            break
        self.model.summary()

    def export(self):
        t = time.time
        export_path = "/tmp/saved_models/{}".format(int(t))
        self.model.save(export_path, save_format='tf')
        self.model = tf.keras.models.load_model(export_path)


class CollectBatchStats(tf.keras.callbacks.Callback):
    def __init__(self):
        self.batch_losses = []
        self.batch_acc = []

    def on_train_batch_end(self, batch, logs=None):
        self.batch_losses.append(logs['loss'])
        self.batch_acc.append(logs['acc'])
        self.model.reset_metrics()


if __name__ == "__main__":
    model = ShotScaleClassifier(name="inception", test=False)
    # model.test()
    # model.test_batch()
    model.test_batch_features()
