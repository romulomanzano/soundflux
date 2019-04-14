import sys
sys.path.append("..")

import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import soundfile
from scipy import signal
import librosa
import matplotlib.pyplot as plt
import specdisplay
from os import listdir
from os.path import isfile, join
import json
from feature_generation import extract_spectrogram
from scipy.io import wavfile
import scipy.signal as sps

import random
random.seed(7)

n_mels = 128

#amplitude of overlay as a percentage of the fall
power_scale_overlay = 0.25

overlay_file_mapping = {'running_shower' : 'resampled_169659_shower.wav',
               'children_playing' : 'resampled_children_ambiance.wav',
               'group_talk':'resampled_group_talking.wav',
               'white_noise_med_pitch':'resampled_white_noise_med_pitch.wav',
               'white_noise_low_pitch':'resampled_white_noise_low_pitch.wav',
               'background_music':'resampled_random_hip_hop.wav'}

#number of randomly selected overlays per file
overlays_per_overlay_file=5
def get_overlay_scaler(normal_file, overlay_file,power_scale_overlay=0.2):
    max_normal = max(np.max(normal_file),-np.min(normal_file))
    max_overlay = max(np.max(overlay_file),-np.min(overlay_file))
    scale_factor = (max_normal*power_scale_overlay)/ max_overlay
    return scale_factor

def get_random_section_of_x_length(overlay_data, size):
    starting_points = (overlay_data.shape[0]-size)
    start = random.choice(range(0,starting_points+1))
    subset = overlay_data[start:start+size]
    return subset

samples_folder = "/home/romulo/github/soundflux/samples"

metadata = [samples_folder+"/"+ f for f in listdir(samples_folder) if isfile(join(samples_folder, f)) and ".json" in f]

data = []
error_count = 0
for fi in metadata:
    log = open(fi, "r").read()
    try:
        d = json.loads(log)
        if isinstance(d,dict):
            data.append(d)
    except Exception as e:
        error_count +=1
        print("Error number {}".format(error_count))

dataset = pd.DataFrame(data)

target_folder = "/home/romulo/Documents/soundflux_augmented_250bps"

split=True
test_split = 0.20

def create_and_save_spectrogram(y,sr,target_file):
    #new plot
    log_s = extract_spectrogram(y,sr,n_mels=n_mels,n_fft=2048)
    fig = plt.figure(figsize=(12,4))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    #getting spectrogram
    specdisplay.specshow(log_s, sr=sr, x_axis='time', y_axis='mel')

    #Saving PNG
    plt.savefig(target_file)
    plt.close()
print("Number of unfiltered rows. {}".format(dataset.shape[0] ))
dataset = dataset[dataset['class'].isin(["falling_dummy", "falling_object"])].reset_index()
print("Number of filtered rows. {}".format(dataset.shape[0]))

for index, row in dataset[::].iterrows():
    print("Transforming file {}".format(index))
    if not os.path.exists(target_folder + "/" + 'spectrograms'):
        os.makedirs(target_folder + "/" + 'spectrograms')
    file_folder = str(target_folder + "/" + 'spectrograms')
    if split:
        if not os.path.exists(file_folder + "/" + 'split'):
            os.makedirs(file_folder + "/" + 'split')
        # 30% on testing
        split_folder = file_folder + "/" + 'split'
        if not os.path.exists(split_folder + "/" + 'train'):
            os.makedirs(split_folder + "/" + 'train')
        if not os.path.exists(split_folder + "/" + 'test'):
            os.makedirs(split_folder + "/" + 'test')
        if random.randint(0, 99) < test_split * 100:
            file_folder = split_folder + '/test'
        else:
            file_folder = split_folder + '/train'

    if not os.path.exists(file_folder + "/" + row['class']):
        os.makedirs(file_folder + "/" + row['class'])
    if not os.path.exists(file_folder + "/overlay_noise"):
        os.makedirs(file_folder + "/overlay_noise")

    # Convert to log scale (dB). We'll use the peak power as reference.
    y, sr = soundfile.read(samples_folder + "/" + str(row['audio_file']))
    target_file_name = file_folder + '/' + row['class'] + '/' + row['id'] + '.png'
    # save original spectrogram
    create_and_save_spectrogram(y, sr, target_file_name)
    # pick one channel from the recorded sample:
    for k, v in overlay_file_mapping.items():
        y_mono = np.squeeze(y[:, :1])
        overlay_data, overlay_sampling_rate = soundfile.read("./overlay_files/{}".format(v))
        if overlay_sampling_rate != sr:
            # assumes sr is greater
            rate = int(sr / overlay_sampling_rate)
            y_mono_base = sps.decimate(y_mono, 3)
        else:
            y_mono_base = y_mono
        for idx in range(0, overlays_per_overlay_file):
            random_overlay = get_random_section_of_x_length(overlay_data, y_mono_base.shape[0])
            scale_factor = get_overlay_scaler(y_mono_base, random_overlay, power_scale_overlay)
            final_overlayed_data = np.add(y_mono_base, scale_factor * random_overlay)
            # write to temp and read again, otherwise data is messed up
            temp_overlay_wav_file = "temp_overlay.wav"
            wavfile.write(temp_overlay_wav_file, overlay_sampling_rate, final_overlayed_data.T)
            # read and generate spectrogram
            combined_sound, combined_sample_rate = soundfile.read(temp_overlay_wav_file)
            overlayed_target_file_name = file_folder + '/' + row['class'] + '/' + row[
                'id'] + '_{}_{}_overlay.png'.format(k, idx)
            create_and_save_spectrogram(combined_sound, combined_sample_rate, overlayed_target_file_name)
            # save original overlay too!
            overlay_target_file_name = file_folder + '/' + "overlay_noise" + '/' + row[
                'id'] + '{}_{}_overlay_only.png'.format(k, idx)
            create_and_save_spectrogram(random_overlay, overlay_sampling_rate, overlay_target_file_name)
    with open('where_we_are.txt','w') as f:
        f.write("File number{}".format(index))
