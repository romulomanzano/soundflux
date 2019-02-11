from threading import Thread
from config import *
import matplotlib.pyplot as plt
import smbus
import time
import os
from accelerometer import Accelerometer
from soundflux import SoundFlux
import soundfile
import tempfile
import wave
import numpy as np
import json
import datetime


class SampleRecorder(object):

    def __init__(self):
        self.acc = Accelerometer()
        self.mic = SoundFlux()
        self.sample_audio = None
        self.sample_vibration = None
        self.sample_length = None

    def get_audio_as_samples(self):
        fp, output_file = tempfile.mkstemp()
        try:
            with wave.open(output_file, 'wb') as wave_file:
                wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
                wave_file.setsampwidth(self.sample_length)
                wave_file.setframerate(MIC_RATE)
                wave_file.writeframes(b''.join(self.sample_audio))
                samples, sample_rate = soundfile.read(output_file)
        finally:
            os.remove(output_file)
        return samples

    def capture_x_seconds_audio(self, seconds):
        self.sample_audio = self.mic.record_x_seconds(seconds)

    def capture_x_seconds_vibration(self, seconds,omit):
        if not omit:
            self.sample_vibration = self.acc.capture_x_seconds(seconds)
        else:
            self.sample_vibration = None

    def capture_x_seconds(self, seconds, exclude_vibration=False, wait=True):
        self.sample_length = seconds
        mic_thread = Thread(target=self.capture_x_seconds_audio, args=[seconds])
        acc_thread = Thread(target=self.capture_x_seconds_vibration, args=[seconds, exclude_vibration])
        mic_thread.daemon = True
        acc_thread.daemon = True
        mic_thread.start()
        acc_thread.start()
        tic = time.time()
        if wait:
            mic_thread.join()
            acc_thread.join()
        toc = time.time()
        print("Time to finish {}".format(toc - tic))

    def save_sample(self, prefix, _class_name, metadata={}):
        base_path = './samples/'
        now = datetime.datetime.utcnow()
        id = str((now - datetime.datetime(1970, 1, 1)).total_seconds())
        base_file_name = "{}_id_{}".format(prefix, id)
        audio_file_name = "{}.wav".format(base_file_name)
        detail_file_name = "{}_index.json".format(base_file_name)
        vibration_file_name = "{}_vibration.json".format(base_file_name)
        file_details = {'id': id, 'class': _class_name, 
                        'timestamp': now.strftime("%m/%d/%Y, %H:%M:%S"), 
                        'prefix': prefix,
                        'audio_file': audio_file_name,
                        'vibration_file': vibration_file_name, 'index_file': detail_file_name,
                        'sample_length' : self.sample_length,
                        'metadata': metadata}
        # index file
        with open(base_path + detail_file_name, 'w') as fp:
            json.dump(file_details, fp)
        if self.sample_vibration:
            # vibration_file
            with open(base_path + vibration_file_name, 'w') as fp:
                json.dump(file_details, fp)
        else:
            file_details.pop('vibration_file')
        ##Save wav file
        with wave.open(base_path + audio_file_name, 'wb') as wave_file:
            wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
            wave_file.setsampwidth(self.sample_length)
            wave_file.setframerate(MIC_RATE)
            wave_file.writeframes(b''.join(self.sample_audio))
        return file_details

    def plot_sample(self):
        if self.sample_vibration:
            plt.plot([s['x'] for s in self.sample_vibration])
            plt.ylabel('X Acceleration')
            plt.show()

            plt.plot([s['y'] for s in self.sample_vibration])
            plt.ylabel('Y Acceleration')
            plt.show()

            plt.plot([s['z'] for s in self.sample_vibration])
            plt.ylabel('Z Acceleration')
            plt.show()

        plt.plot(list(np.mean(self.get_audio_as_samples(), axis=1)))
        plt.ylabel('Audio')
        plt.show()
