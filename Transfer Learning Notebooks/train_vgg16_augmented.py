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
approx_fold_size = 9000

train_folder = "/home/nvidia/Downloads/soundflux_augmented/spectrograms/split/train/"
test_folder = "/home/nvidia/Downloads/soundflux_augmented/spectrograms/split/test/"


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
fall_dummy_class_weight = 1.0
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
                          steps_per_epoch=approx_fold_size/batch_size,
                          validation_data = test_generator,
                          validation_steps = 1000/batch_size,
                          epochs=10,
                          shuffle=True, 
                          verbose=True,
                          class_weight=class_weight)


test_generator = datagen.flow_from_directory(test_folder,
                                          target_size = (img_height,img_width),
                                          class_mode = 'categorical',
                                          batch_size = batch_size,
                                          shuffle=True,
                                          seed=7)

results = model.evaluate_generator(test_generator,
                              steps=1000/batch_size,
                              verbose=True)
print(results)

#save model

model.save_weights('augmented_model_three_classes_unfrozen_layers_weighted_v4.h5')
model_json = model.to_json()
with open("augmented_model_three_classes_unfrozen_layers_weighted_v4.json", "w") as json_file:
    json_file.write(model_json)
with open("augmented_model_three_classes_unfrozen_layers_weighted_v4_class_indices.json", "w") as json_file:
    train_generator.class_indices
    json_file.write(json.dumps(train_generator.class_indices))
