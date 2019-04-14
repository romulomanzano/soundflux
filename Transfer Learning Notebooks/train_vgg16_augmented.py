import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
set_session(sess)

from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import json
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd

def save_plots(history,target_file_acc,target_file_loss):
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(target_file_acc)
    plt.close()
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(target_file_loss)
    plt.close()

def show_plots(history):
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

batch_size = 32
img_height=80
img_width = 256

train_folder = "/home/nvidia/Downloads/soundflux_augmented_250bps/spectrograms/split/train/"
test_folder = "/home/nvidia/Downloads/soundflux_augmented_250bps/spectrograms/split/test/"


datagen = ImageDataGenerator(rescale=1./255,
                            #rotation_range=10,
                            width_shift_range=0.2,
                            height_shift_range=0.1,
                            shear_range=0.2,
                            zoom_range=0.3,
                            #horizontal_flip=True,
                            #vertical_flip=True,
                            fill_mode='nearest')

input_shape = (img_height, img_width,3)
nclass = 3

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import optimizers

base_model = keras.applications.vgg16.VGG16(weights='imagenet', 
                                include_top=False, 
                                input_shape=(img_height, img_width,3))

#base_model.trainable = False
for layer in base_model.layers[:15]:
    layer.trainable = False
"""   #Adding custom Layers
"""
model = keras.models.Sequential()
model.add(base_model)
model.add(keras.layers.GlobalAveragePooling2D())
model.add(keras.layers.Dense(512,activation='relu'))
model.add(keras.layers.Dense(64,activation='relu'))
model.add(keras.layers.Dense(32,activation='relu'))
model.add(keras.layers.Dropout(0.5))
model.add(keras.layers.Dense(nclass, activation='softmax'))


opt = optimizers.RMSprop(lr=0.0001,decay=1e-3)
#opt = optimizers.Adam(lr=0.001)
model.compile(loss='categorical_crossentropy', 
              optimizer=opt,
              metrics=['accuracy'])
#needed to reset weigh"""ts!
model.summary()


train_generator = datagen.flow_from_directory(train_folder,
                                          target_size = (img_height,img_width),
                                          class_mode = 'categorical',
                                          batch_size = batch_size,
                                          shuffle=True, 
                                          seed=7)

test_generator = datagen.flow_from_directory(test_folder,
                                          target_size = (img_height,img_width),
                                          class_mode = 'categorical',
                                          batch_size = batch_size,
                                          shuffle=True, 
                                          seed=7)

#RESET WEIGHTS!!
#model.load_weights('raw_model.h5')
#Augment class weights!
fall_dummy_class_weight = 1.5
class_weight = {}
for k,v in train_generator.class_indices.items():
    if k == "falling_dummy":
        class_weight[v] = fall_dummy_class_weight
    else:
        class_weight[v] = 1.0

print("Class weights: {}".format(class_weight))
#Idea of the above is to generate class_weight = {0: 2.0, 1: 1.0, 2: 1.0}
#
history = model.fit_generator(train_generator,
                          steps_per_epoch=np.ceil(len(train_generator.classes)/(2*batch_size)),
                          validation_data = test_generator,
                          validation_steps = np.ceil(len(test_generator.classes)/batch_size),
                          epochs=6,
                          shuffle=True, 
                          verbose=True,
                          class_weight=class_weight)


test_generator = datagen.flow_from_directory(test_folder,
                                          target_size = (img_height,img_width),
                                          class_mode = 'categorical',
                                          batch_size = batch_size,
                                          shuffle=True,
                                          seed=7)

predictions = model.predict_generator(test_generator,
                              steps=np.ceil(len(test_generator.classes)/batch_size),
                              verbose=True)
y_pred = np.argmax(predictions, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(test_generator.classes, y_pred)
normalized = cm/cm.sum(axis=1)[:, np.newaxis]
print(normalized)

#save model
#v1 no class weight, ran on the 20% overlay
#v2 added 3x class weight on falling_dummy ran on the 20% overlay
#v3 was essentially v2 but with a 2x class weight on falling_dummy ran on the 20% overlay
#v4 will be with 35% overlay on source files
#v5 will be with 25% overlay on source files
#v6 is 20% overlay with 1.5 weight on dummy class
#v7 same as v6 but with 250bps
model.save_weights('augmented_model_three_classes_unfrozen_layers_weighted_v7.h5')
model_json = model.to_json()
with open("augmented_model_three_classes_unfrozen_layers_weighted_v7.json", "w") as json_file:
    json_file.write(model_json)
with open("augmented_model_three_classes_unfrozen_layers_weighted_v7_class_indices.json", "w") as json_file:
    train_generator.class_indices
    json_file.write(json.dumps(train_generator.class_indices))

#evaluate on stress test
stress_test_folder = "/home/nvidia/Downloads/soundflux_stress_testing/spectrograms/"
stress_test_generator = datagen.flow_from_directory(stress_test_folder,
                                          target_size = (img_height,img_width),
                                          class_mode = 'categorical',
                                          batch_size = batch_size,
                                          shuffle=False, 
                                          seed=7)

stress_predictions = model.predict_generator(stress_test_generator,
                              steps=np.ceil(len(stress_test_generator.classes)/batch_size),
                              verbose=True)
stress_y_pred = np.argmax(stress_predictions, axis=1)
mapped_results = []
for i in y_pred:
    r_map = {}
    for k, v in train_generator.class_indices.items():
        if i == v:
            mapped_results.append(str(k))
            break
print(np.mean([x=="falling_object" for x in mapped_results]))

