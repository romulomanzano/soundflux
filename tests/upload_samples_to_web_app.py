import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

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
import requests
from config import *
import base64
import datetime

def register_samples():
    samples_folder = "/home/romulo/github/soundflux/samples"
    target_folder = "/media/romulo/6237-3231/randy_samples"
    metadata = [samples_folder + "/" + f for f in listdir(samples_folder) if
                isfile(join(samples_folder, f)) and ".json" in f]
    n_mels = 128
    data = []
    error_count = 0
    for fi in metadata:
        log = open(fi, "r").read()
        try:
            d = json.loads(log)
            data.append(d)
        except Exception as e:
            error_count += 1
            print("Error number {}".format(error_count))
    dataset = pd.DataFrame(data)
    for index, row in dataset[::].iterrows():
        try:
            print("Transforming file {}".format(index))
            # Convert to log scale (dB). We'll use the peak power as reference.
            y, sr = soundfile.read(samples_folder + "/" + str(row['audio_file']))
            log_s = extract_spectrogram(y, sr, n_mels=n_mels, n_fft=2048)
            # new plot
            fig = plt.figure(figsize=(12, 4))
            ax = plt.Axes(fig, [0., 0., 1., 1.])
            ax.set_axis_off()
            fig.add_axes(ax)

            # getting spectrogram
            specdisplay.specshow(log_s, sr=sr, x_axis='time', y_axis='mel')

            # Saving PNG
            plt.savefig(target_folder + "/" + 'spectrograms/' + row['class'] +
                        '/' + row['id'] + '.png')
            plt.close()
            #Upload to Target
            binary_data = open(target_folder + "/" + 'spectrograms/' + row['class'] +
                        '/' + row['id'] + '.png', 'rb').read()
            base64_bytes = base64.b64encode(binary_data)
            bstring = base64_bytes.decode('utf-8')
            if isinstance(row['metadata'],dict):
                metadata = row['metadata']
            else:
                metadata={}
            order_by_field = datetime.datetime.strptime(row['timestamp'], "%m/%d/%Y, %H:%M:%S").timestamp()
            request_data = {
                        "sample_details" : {
                            "metadata" : {
                                "sample_lenght" : row['sample_length'],
                                "distance_from_device": metadata.get('distance_from_device'),
                                "floor_type": metadata.get('floor_type'),
                                "timestamp" : row['timestamp'],
                                "time_order_desc" : -order_by_field
                            },
                            "sample_type" : "training_data",
                            "label" : row['class'],
                            "model_prediction" : {},
                            "spectrogram" : bstring
                        },
                        "device_id" : SOUNDFLUX_DEVICE_ID
                    }
            url = "https://api.soundflux.io/api/sample/register"
            headers = {'Content-Type': 'application/json',
                       'Authorization': "Bearer " + SOUNDFLUX_SOUNDFLUX_ACCOUNT_TOKEN,
                       'Email' : SOUNDFLUX_ACCOUNT_EMAIL}
            r = requests.post(url, json=request_data, headers=headers)
            print(r.status_code, (r.status_code == 201),r.text)
            #print(request_data)
        except Exception as e:
            print("Error {}".format(e))

if __name__ == '__main__':
    arg = sys.argv[1]
    if arg == "upload":
        register_samples()