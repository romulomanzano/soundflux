import sys
from tensorflow import keras
import pandas as pd
import numpy as np
import timeit

def simple_mfcc_aggregation(mfccs):
        return np.mean(mfccs, axis=0)

def test_predict():
    with open('../trained_models/hdf5/urban_sound_model.json', 'r') as json_file:
        loaded_model_json = json_file.read()
    loaded_model = keras.models.model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("../trained_models/hdf5/urban_sound_model.h5")
    print("Loaded model from disk")
    # evaluate loaded model on test data
    loaded_model.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    #Load test data to evaluate
    sample_data = pd.read_json('./urban_sound_mfcc_sample/mfcc_labeled_samples.json')
    x_sample = []
    for x in sample_data.feature.tolist():
        x_sample.append(simple_mfcc_aggregation(x))
    x_sample_array = np.array(x_sample)
    y_sample_array = np.array(sample_data.label_encoded.tolist())
    #Time it
    start = timeit.default_timer()
    score = loaded_model.evaluate(x_sample_array, y_sample_array, verbose=0)
    stop = timeit.default_timer()
    print('Time to evaluate model using keras', stop - start)
    print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))


if __name__ == '__main__':
    test_predict()
