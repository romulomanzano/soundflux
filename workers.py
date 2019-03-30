from config import *
from datetime import datetime as dt
import matplotlib.pyplot as plt
from feature_generation import extract_spectrogram
import specdisplay
import wave
import soundfile
import time
import json
import os
from os import listdir
from os.path import isfile
import utils
import inference
from shutil import copyfile

logger = utils.get_generic_logger(__name__)

def vibration_capture_worker(acc, acc_queue, go, sample_frequency_hertz=ACC_FREQUENCY_HZ,
                             gforce=True, apply_scaler=True):
    """
    This function will enable continuous recording through the device, while writing to a buffer
    every segment
    :param acc: Accelerometer object
    :param qo: Queue object to store captured sound windows
    :param go: bool run signal from spawning process
    :return: None
    """
    while True:
        ax = acc.get_axes(gforce=gforce, apply_scaler=apply_scaler)
        acc_queue.put(ax)
        time.sleep(1.0 / sample_frequency_hertz)
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
                                  n_mels=128, n_fft=2048, inference_window=5, seconds_between_samples=0.4):
    """
    This function will enable continuous transformation of raw input to transformed features.
    It will return either a single timestep feature array, or a full nd array.
    :param qi: Queue object to get audio samples
    :param qo: Queue object to put features
    :param go: bool run signal from spawning process
    :param inference_window: float number of seconds to process in a single spectrogram
    :return: None
    """
    frames_in_window = int((MIC_RATE / MIC_PERIOD_SIZE_LIVE_FEED) * inference_window)
    frames = []
    frames_to_be_shifted = int((MIC_RATE / MIC_PERIOD_SIZE_LIVE_FEED) * seconds_between_samples)
    while True:
        # shift frames
        if len(frames) >= frames_in_window:
            frames = frames[frames_to_be_shifted:]
        for step in range(frames_to_be_shifted):
            if go.value == 0 and sound_queue.empty():
                return
            # compile enough samples to make a complete spectrogram for inference
            frames.append(sound_queue.get())
        #extract if enough frames in the file
        if len(frames) >= frames_in_window:
            now = dt.utcnow()
            # save wave
            with wave.open(LIVE_FEED_TARGET_FOLDER + "/{}_recorded_sample.wav".format(now.timestamp()), 'wb') as wave_file:
                wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
                wave_file.setsampwidth(TARGET_FILE_SAMPLE_WIDTH)
                wave_file.setframerate(MIC_RATE)
                wave_file.writeframes(b''.join(frames))
            # read from file
            y, sr = soundfile.read(LIVE_FEED_TARGET_FOLDER + "/{}_recorded_sample.wav".format(now.timestamp()))
            # spectrogram
            spec = extract_spectrogram(y, sample_rate=sr, n_mels=n_mels, n_fft=n_fft)
            if save_features:
                fig = plt.figure(figsize=(12, 4))
                ax = plt.Axes(fig, [0., 0., 1., 1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                # getting spectrogram
                specdisplay.specshow(spec, sr=sample_rate, x_axis='time', y_axis='mel')
                # Saving PNG
                plt.savefig(LIVE_FEED_TARGET_FOLDER + "/{}_mel_spectrogram.png".format(now.timestamp()))
                plt.close()


def extract_vibration_features_worker(acc_queue, go, save_features, inference_queue,
                                      sample_frequency_hertz=ACC_FREQUENCY_HZ,
                                      inference_window=1, seconds_between_samples=1,
                                      inference_threshold = LIVE_FEED_INFERENCE_ACC_THRESHOLD):
    """
    This function will enable continuous transformation of raw input to transformed features.
    It will return either a single timestep feature array, or a full nd array.
    :param qi: Queue object to get audio samples
    :param qo: Queue object to put features
    :param go: bool run signal from spawning process
    :param inference_window: float number of seconds to process in a single spectrogram
    :return: None
    """
    frames_in_window = int(sample_frequency_hertz * inference_window)
    frames = []
    frames_to_be_shifted = int(sample_frequency_hertz * seconds_between_samples)
    while True:
        # shift frames
        if len(frames) >= frames_in_window:
            frames = frames[frames_to_be_shifted:]
        logger.info("Len for frames {}".format(len(frames)))
        for step in range(frames_to_be_shifted):
            if go.value == 0 and acc_queue.empty():
                return
            # compile enough samples to make a complete spectrogram for inference
            frames.append(acc_queue.get())

        if len(frames) >= frames_in_window:
            now = dt.utcnow()
            logger.info("Should save now")
            # check vibration thresholds
            max_x, max_y, max_z = 0, 0, 0
            for k in frames:
                # max and keep the sign
                max_x = max(abs(k.get('x', 0)), max_x)
                max_y = max(abs(k.get('y', 0)), max_y)
                max_z = max(abs(k.get('z', 0)), max_z)
            if save_features:
                vibration_file_name = LIVE_FEED_TARGET_FOLDER + "/{}_vibration.json".format(now.timestamp())
                with open(vibration_file_name, 'w') as fp:
                    json.dump({'max_x': max_x, 'max_y': max_y, 'max_z': max_z}, fp)
            if max(max_x, max_y, max_z) >= inference_threshold:
                logger.info("Threshold of {} exceeded. Acc read x, y, z: {}, {}, {}".format(inference_threshold,
                                                                round(max_x, 2), round(max_y, 2), round(max_z, 2)))
                inference_queue.put({'timestamp': now.timestamp(), 'max_x': max_x, 'max_y': max_y, 'max_z': max_z})
                if go.value == 0:
                    return

def inference_worker(inference_queue, go):
    #prep model
    inf = inference.SoundInference()
    inference_folder = LIVE_FEED_INFERENCE_FOLDER

    while True:
        # shift frames
        if go.value == 0 and inference_queue.empty():
            return
        now = dt.utcnow().timestamp()
        time.sleep()
        details = inference_queue.get()
        #move relevant files to live feed folder
        spectrograms = [f for f in listdir(LIVE_FEED_TARGET_FOLDER)
                 if isfile(os.path.join(LIVE_FEED_TARGET_FOLDER, f)) and (".png" in f)]
        inference_files = []
        for file in spectrograms:
            try:
                timestamp = float(file[:16])
                if abs(now - timestamp) >= LIVE_FEED_SPECTROGRAM_WINDOW_SECONDS:
                    copyfile(os.path.join(LIVE_FEED_TARGET_FOLDER, file),
                             os.path.join(LIVE_FEED_INFERENCE_FOLDER, file))
                    inference_files.append(file)
            except:
                logger.info("Can't extract timestamp from filename: {}".format(file))
        #TODO: actually ping the server with results!
        results = inf.predict_img_classes_from_folder(LIVE_FEED_INFERENCE_FOLDER)
        for file in inference_files:
            try:
                os.remove(os.path.join(LIVE_FEED_INFERENCE_FOLDER, file))
            except:
                logger.info("Can't remove file from {} : {}".format(file, LIVE_FEED_INFERENCE_FOLDER))

def garbage_collection_worker(purge_older_than_n_seconds, go):
    while True:
        if go.value == 0:
            return
        now = dt.utcnow().timestamp()
        files = [f for f in listdir(LIVE_FEED_TARGET_FOLDER)
                 if isfile(os.path.join(LIVE_FEED_TARGET_FOLDER, f))
                 and ((".json" in f) or (".wav" in f) or (".png" in f))]
        for file in files:
            try:
                timestamp = float(file[:16])
                if now - timestamp >= purge_older_than_n_seconds:
                    os.remove(os.path.join(LIVE_FEED_TARGET_FOLDER, file))
            except:
                logger.info("Can't extract timestamp from filename: {}".format(file))
        time.sleep(purge_older_than_n_seconds)
