import numpy as np
import imageio
import librosa
from config import *
from datetime import datetime as dt
import matplotlib.pyplot as plt
from feature_generation import extract_spectrogram
import specdisplay
import wave
import soundfile

def data_capture_worker(mic, acc, qo, go):
    """
    This function will enable continuous recording through the device, while writing to a buffer
    every segment
    :param mic: SoundFlux object
    :param qo: Queue object to store captured sound windows
    :param go: bool run signal from spawning process
    :return: None
    """
    while True:

        l, data = mic.recorder.read()
        array = np.frombuffer(data, dtype = np.dtype('>i4'))
        channeled_array = np.reshape(array, (4, int(MIC_PERIOD_SIZE_LIVE_FEED)), order="F")
        mean_signal = np.mean(channeled_array, axis=0)
        qo.put(mean_signal)
        
        if go.value == 0:
            return


def audio_capture_worker(mic, sound_queue, go):
    """
    This function will enable continuous recording through the device, while writing to a buffer
    every segment
    :param mic: SoundFlux object
    :param qo: Queue object to store captured sound windows
    :param go: bool run signal from spawning process
    :return: None
    """
    while True:

        l, data = mic.recorder.read()
        sound_queue.put(data)
        if go.value == 0:
            return


def extract_audio_features_worker(sound_queue, go, save_features, sample_rate=16000,
                            n_mels=128, n_fft=2048, inference_window=5, seconds_between_samples = 0.4):
    """
    This function will enable continuous transformation of raw input to transformed features.
    It will return either a single timestep feature array, or a full nd array.
    :param qi: Queue object to get audio samples
    :param qo: Queue object to put features
    :param go: bool run signal from spawning process
    :param inference_window: float number of seconds to process in a single spectrogram
    :return: None
    """
    frames_in_window = int((MIC_RATE/MIC_PERIOD_SIZE_LIVE_FEED)* inference_window)
    frames = []
    frames_to_be_shifted = int((MIC_RATE/MIC_PERIOD_SIZE_LIVE_FEED) * seconds_between_samples)
    while True:
        # shift frames
        if len(frames) >= frames_in_window:
            frames = frames[frames_to_be_shifted:]
        print("Len for frames {}".format(len(frames)))
        for step in range(frames_to_be_shifted):
            if go.value==0 and sound_queue.empty():
                return
            # compile enough samples to make a complete spectrogram for inference
            frames.append(sound_queue.get())
            print(len(frames),step)

        if len(frames) >= frames_in_window:
            print("Should save now")
            now = dt.now()
            #save wave
            with wave.open("recorded_sample_{}.wav".format(now), 'wb') as wave_file:
               wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
               wave_file.setsampwidth(TARGET_FILE_SAMPLE_WIDTH)
               wave_file.setframerate(MIC_RATE)
               wave_file.writeframes(b''.join(frames))
            #read from file
            y, sr = soundfile.read("recorded_sample_{}.wav".format(now))
            #spectrogram
            spec = extract_spectrogram(y, sample_rate=sr,n_mels=n_mels,n_fft=n_fft)
            if save_features:
                fig = plt.figure(figsize=(12, 4))
                ax = plt.Axes(fig, [0., 0., 1., 1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                # getting spectrogram
                specdisplay.specshow(spec, sr=sample_rate, x_axis='time', y_axis='mel')
                # Saving PNG
                plt.savefig("mel_spectrogram_{}.png".format(now))
                plt.close()

                
def extract_features_worker(sound_queue, go, save_spectrograms, sample_rate=16000,
                            n_mels=128, n_fft=2048, inference_window=1):
    """
    This function will enable continuous transformation of raw input to transformed features.
    It will return either a single timestep feature array, or a full nd array.
    :param qi: Queue object to get audio samples
    :param qo: Queue object to put features
    :param go: bool run signal from spawning process
    :param inference_window: float number of seconds to process in a single spectrogram
    :return: None
    """
    samples_in_window = MIC_RATE*inference_window
    window = np.zeros(samples_in_window)

    while True:
        # move second half of data to beginning then fill the second half with a for loop
        window.put(range(int(samples_in_window/2)), window.take(range(int(samples_in_window/2), samples_in_window)))
        for step in range(int(samples_in_window/(MIC_PERIOD_SIZE_LIVE_FEED*2))):
            if go.value==0 and sound_queue.empty():
                return

            # compile enough samples to make a complete spectrogram for cnn inference
            window.put(range(int(samples_in_window/2 + step*MIC_PERIOD_SIZE_LIVE_FEED),
                        int(samples_in_window/2 + (step+1)*MIC_PERIOD_SIZE_LIVE_FEED)),
                        sound_queue.get())

        if np.max(window) > MIN_VOLUME_FOR_INFERENCE:
            spec = extract_spectrogram(window, sample_rate=sample_rate,n_mels=n_mels,n_fft=n_fft)

            if save_spectrograms:
                fig = plt.figure(figsize=(12, 4))
                ax = plt.Axes(fig, [0., 0., 1., 1.])
                ax.set_axis_off()
                fig.add_axes(ax)

                # getting spectrogram
                specdisplay.specshow(spec, sr=sample_rate, x_axis='time', y_axis='mel')
                # Saving PNG
                plt.savefig("mel_spectrogram_{}.png".format(dt.now()))
                plt.close()

