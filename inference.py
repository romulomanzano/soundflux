from config import *
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.preprocessing.image import ImageDataGenerator
from keras.models import model_from_json
from keras.preprocessing import image
import numpy as np
import json
import utils
import sys
from notification import register_inference
import math

@utils.logged
class SoundInference(object):

    def __init__(self, model_definition_location=SOUNDFLUX_MODEL_DEFINITION_LOCATION,
                 model_weights_location=SOUNDFLUX_MODEL_WEIGHTS_LOCATION,
                 model_labels_location=SOUNDFLUX_MODEL_LABELS_MAP_LOCATION,
                 img_height=80, img_width = 256):
        #prep for inference
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        set_session(sess)
        self.img_height = img_height
        self.img_width = img_width
        # load json and create model
        with open(model_definition_location, 'r') as json_file:
            loaded_model_json = json_file.read()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights(model_weights_location)
        self.logger.info("Loaded model from disk")
        with open(model_labels_location, 'r') as json_file:
            label_map = json.load(json_file)
        self.label_map = label_map
        self.logger.info("Loaded label mappings: {}".format(self.label_map))

    def _get_predict_generator(self, folder):
        datagen = ImageDataGenerator(rescale=1. / 255)
        gen = datagen.flow_from_directory(folder,
                             target_size=(self.img_height, self.img_width),
                             class_mode='categorical',
                            batch_size=1,
                            shuffle=False)
        return gen

    def _map_inference_to_labels(self,results, filenames):
        map = dict(self.label_map)
        mapped_results = []
        likely_class = None
        likely_class_probability = 0
        for i, item in enumerate(results):
            r_map = {}
            for k, v in map.items():
                proba = float(item[v])
                r_map[k] = float(proba)
                if (proba>likely_class_probability):
                    likely_class = str(k)
                    likely_class_probability = float(proba)
            r_map['filename'] = filenames[i]
            mapped_results.append(r_map)
            self.logger.info("******Predicted Class: {} with {}% probability******" \
                .format(likely_class, round(math.floor(likely_class_probability*10000)/100,1)))
        return mapped_results

    def predict_img_classes_from_folder(self, folder, batch=4):
        self.logger.info('Looking for files in folder {}'.format(folder))
        generator = self._get_predict_generator(folder)
        filenames = list(generator.filenames)
        results = self.model.predict_generator(generator, batch, verbose=True)
        mapped_results = self._map_inference_to_labels(results, filenames)
        self.logger.info('Full inference results: {}'.format(mapped_results))
        return mapped_results

    def load_image(self, image_url):
        img = image.load_img(image_url, target_size=(self.img_height, self.img_width))
        img_tensor = image.img_to_array(img)  # (height, width, channels)
        img_tensor = np.expand_dims(img_tensor, axis=0)  # (1, height, width, channels)
        img_tensor /= 255.  # imshow expects values in the range [0, 1]
        return img_tensor

    def predict_image(self, image_url):
        self.logger.info('Running inference on image {}'.format(image_url))
        img_tensor = self.load_image(image_url)
        results = self.model.predict(img_tensor, verbose=True)
        mapped_results = self._map_inference_to_labels(results, [image_url])
        self.logger.info('Inference results: {}'.format(mapped_results))
        return mapped_results

if __name__ == '__main__':
    arg = sys.argv[1]
    if arg == "run_test":
        inf = SoundInference()
        test_folder = SOUNDFLUX_MODEL_TEST_IMAGE_FOLDER
        inf.predict_img_classes_from_folder(test_folder)
