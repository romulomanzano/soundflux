from config import *
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.preprocessing.image import ImageDataGenerator
import keras
import utils
import sys

@utils.logged
class SoundInference(object):

    def __init__(self, model="VGG16", model_weights_location=SOUNDFLUX_MODEL_WEIGHTS_LOCATION,
                 img_height=80, img_width = 256):
        #prep for inference
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        set_session(sess)
        self.img_height = img_height
        self.img_width = img_width
        if model == "VGG16":
            base_model = keras.applications.vgg16.VGG16(weights='imagenet',
                                                    include_top=False,
                                                    input_shape=(img_height, img_width, 3))
            for layer in base_model.layers[:15]:
                layer.trainable = False
            """   #Adding custom Layers
               x = model.output
               x = Flatten()(x)
               x = Dense(4096, activation="relu")(x)
               x = Dropout(0.5)(x)
               x = Dense(4096, activation="relu")(x)
               x = Dropout(0.5)(x)
            """
            seq_model = keras.models.Sequential()
            seq_model.add(base_model)
            seq_model.add(keras.layers.GlobalAveragePooling2D())
            seq_model.add(keras.layers.Dense(512, activation='relu'))
            seq_model.add(keras.layers.Dense(64, activation='relu'))
            seq_model.add(keras.layers.Dense(32, activation='relu'))
            seq_model.add(keras.layers.Dropout(0.5))
            seq_model.add(keras.layers.Dense(5, activation='softmax'))
            self.model = seq_model
            self.model.load_weights(model_weights_location)


    def _get_predict_generator(self, folder):
        datagen = ImageDataGenerator(rescale=1. / 255)
        gen = datagen.flow_from_directory(folder,
                             target_size=(self.img_height, self.img_width),
                             class_mode='categorical',
                            batch_size=1)

        return gen

    def predict_img_classes_from_folder(self, folder):
        generator = self._get_predict_generator(folder)
        results = self.model.predict_generator(generator, 4, verbose=True)
        self.logger.info('Inference results: {}'.format(results))
        return results


if __name__ == '__main__':
    arg = sys.argv[1]
    if arg == "run_test":
        inf = SoundInference()
        test_folder = SOUNDFLUX_MODEL_TEST_IMAGE_FOLDER
        inf.predict_img_classes_from_folder(test_folder)
