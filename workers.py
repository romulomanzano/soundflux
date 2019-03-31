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
        now = dt.utcnow().timestamp()*1000
        ax = acc.get_axes(gforce=gforce, apply_scaler=apply_scaler)
        acc_queue.put((ax, now))
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
        now = dt.utcnow().timestamp()*1000
        l, data = mic.recorder.read()
        sound_queue.put((data, now))
        if go.value == 0:
            return

def extract_audio_features_worker(sound_queue, go, inference_window=5, seconds_between_samples=0.8):
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
    frames_timestamps = []
    frames_to_be_shifted = int((MIC_RATE / MIC_PERIOD_SIZE_LIVE_FEED) * seconds_between_samples)
    while True:
        # shift frames
        if len(frames) >= frames_in_window:
            frames = frames[frames_to_be_shifted:]
            frames_timestamps = frames_timestamps[frames_to_be_shifted:]
        for step in range(frames_to_be_shifted):
            if go.value == 0 and sound_queue.empty():
                return
            # compile enough samples to make a complete spectrogram for inference
            frame, timestamp = sound_queue.get()
            frames.append(frame)
            frames_timestamps.append(timestamp)
        #extract if enough frames in the file
        if len(frames) >= frames_in_window:
            file_timestamp = frames_timestamps[0]
            # save wave
            with wave.open(LIVE_FEED_TARGET_FOLDER + "/{}_recorded_sample.wav".format(file_timestamp), 'wb') as wave_file:
                wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
                wave_file.setsampwidth(TARGET_FILE_SAMPLE_WIDTH)
                wave_file.setframerate(MIC_RATE)
                wave_file.writeframes(b''.join(frames))

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
    frames_timestamps = []
    frames_to_be_shifted = int(sample_frequency_hertz * seconds_between_samples)
    while True:
        # shift frames
        if len(frames) >= frames_in_window:
            frames = frames[frames_to_be_shifted:]
            frames_timestamps = frames_timestamps[frames_to_be_shifted:]
        for step in range(frames_to_be_shifted):
            if go.value == 0 and acc_queue.empty():
                return
            # compile enough samples to make a complete spectrogram for inference
            frame, timestamp = acc_queue.get()
            frames.append(frame)
            frames_timestamps.append(timestamp)

        if len(frames) >= frames_in_window:
            file_timestamp = frames_timestamps[0]
            # check vibration thresholds
            max_x, max_y, max_z = 0, 0, 0
            for k in frames:
                # max and keep the sign
                max_x = max(abs(k.get('x', 0)), max_x)
                max_y = max(abs(k.get('y', 0)), max_y)
                max_z = max(abs(k.get('z', 0)), max_z)
            if save_features:
                vibration_file_name = LIVE_FEED_TARGET_FOLDER + "/{}_vibration.json".format(file_timestamp)
                with open(vibration_file_name, 'w') as fp:
                    json.dump({'max_x': max_x, 'max_y': max_y, 'max_z': max_z}, fp)
            logger.info("Acc read x, y, z: {}, {}, {}".format(round(max_x, 2), round(max_y, 2), round(max_z, 2)))
            if max(max_x, max_y, max_z) >= inference_threshold:
                logger.info("Threshold of {} exceeded. Acc read x, y, z: {}, {}, {}".format(inference_threshold,
                                                                round(max_x, 2), round(max_y, 2), round(max_z, 2)))
                inference_queue.put({'timestamp': file_timestamp, 'max_x': max_x, 'max_y': max_y, 'max_z': max_z})
                if go.value == 0:
                    return

def inference_worker(inference_queue, go, n_mels=128, n_fft=2048):
    #prep model
    inf = inference.SoundInference()
    if not os.path.exists(LIVE_FEED_INFERENCE_FOLDER + "/"+'unknown'):
        os.makedirs(LIVE_FEED_INFERENCE_FOLDER + "/"+'unknown')
 
    while True:
        # shift frames
        if go.value == 0 and inference_queue.empty():
            return
        details = inference_queue.get()
        now = details.get('timestamp')
        logger.info('Inference triggered, will wait for a few seconds for audio samples to be processed - {}'.format(now))
        #wait until overlapping files are available
        while True:
            audio_samples = [f for f in listdir(LIVE_FEED_TARGET_FOLDER)
                            if isfile(os.path.join(LIVE_FEED_TARGET_FOLDER, f)) and (".wav" in f)]
            #wait until files where the first frame was recorded x seconds after the vibration was detected are available
            tail_audio_samples= [x for x in audio_samples
                                 if float(x[:13])-now >= LIVE_FEED_SPECTROGRAM_WINDOW_SECONDS*1000]
            if tail_audio_samples:
                break
        #move relevant files to live feed folder
        audio_samples = [f for f in listdir(LIVE_FEED_TARGET_FOLDER)
                 if isfile(os.path.join(LIVE_FEED_TARGET_FOLDER, f)) and (".wav" in f)]
        inference_files = []
        logger.info("Generating spectrograms.")
        for file in audio_samples:
            try:
                timestamp = float(file[:13])
                #the data preceeding the vibration isn't as important (for now)
                if (abs(now - timestamp) <= LIVE_FEED_SPECTROGRAM_WINDOW_SECONDS*1000) and \
                    (now - timestamp) <= LIVE_FEED_SPECTROGRAM_WINDOW_SECONDS*250 :
                    #Generate spectrogram!
                    # read from file
                    y, sr = soundfile.read(LIVE_FEED_TARGET_FOLDER + "/" + file)
                    # spectrogram
                    spec = extract_spectrogram(y, sample_rate=sr, n_mels=n_mels, n_fft=n_fft)
                    fig = plt.figure(figsize=(12, 4))
                    ax = plt.Axes(fig, [0., 0., 1., 1.])
                    ax.set_axis_off()
                    fig.add_axes(ax)
                    # getting spectrogram
                    specdisplay.specshow(spec, sr=sr, x_axis='time', y_axis='mel')
                    # Saving PNG
                    inference_file_name = \
                        LIVE_FEED_INFERENCE_FOLDER+"/unknown" + "/{}_mel_spectrogram.png".format(timestamp)
                    plt.savefig(inference_file_name)
                    plt.close()
                    inference_files.append(inference_file_name)
            except:
                logger.info("Can't extract timestamp from filename: {}".format(file))
        #TODO: actually ping the server with results!
        #this will look for folders within the live feed folder, hence will finde the inference folder
        results = inf.predict_img_classes_from_folder(LIVE_FEED_INFERENCE_FOLDER, batch = len(inference_files))
        for file in inference_files:
            try:
                os.remove(file)
            except:
                logger.info("Can't remove file from {} : {}".format(file, LIVE_FEED_INFERENCE_FOLDER))

def garbage_collection_worker(purge_older_than_n_seconds, go):
    while True:
        file_ct = 0
        if go.value == 0:
            return
        now_timestamp = dt.utcnow().timestamp()*1000
        files = [f for f in listdir(LIVE_FEED_TARGET_FOLDER)
                 if isfile(os.path.join(LIVE_FEED_TARGET_FOLDER, f))
                 and ((".json" in f) or (".wav" in f) or (".png" in f))]
        for file in files:
            try:
                timestamp = int(file[:13])
                if now_timestamp - timestamp >= (purge_older_than_n_seconds*1000):
                    os.remove(os.path.join(LIVE_FEED_TARGET_FOLDER, file))
                    file_ct +=1
            except:
                logger.info("Can't extract timestamp from filename: {}".format(file))
        logger.info("Garbage collector - removed a total of {} files".format(file_ct))
        time.sleep(purge_older_than_n_seconds)
