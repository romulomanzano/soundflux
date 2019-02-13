import Queue
import time
from threading import Event, Thread

import numpy as np

import librosa
from accelerometer import Accelerometer
from soundflux import SoundFlux

# Set up some global variables
sound_queue = Queue.Queue()
feature_queue = Queue.Queue()
stop_event = Event()
threads = ["run_sound_capture", "run_feature_extractor", "run_inference"]

def run():
    # Instantiate Objects
    mic = SoundFlux(liveFeed=True)
    acc = Accelerometer()

    run_sound_capture = Thread(target=capture_sound_worker, args=(mic, sound_queue, stop_event,))
    run_feature_extractor = Thread(target=extract_features_worker, args=(mic, sound_queue,)) #TODO Update args
    run_inference = Thread(target=inference_worker, args=(mic, sound_queue,)) #TODO Update args

    for worker in threads:
        worker.setDaemon(True)
        worker.start()

    print("Listening and running inference... Press any key to stop.")
    if input:
        stop_event.set()
    print("Pipeline finishing...")
    for worker in threads:
        while worker.is_alive():
            time.sleep(.25)
    print("Pipeline complete!")

    return 0

def capture_sound_worker(mic, qo, stop_event):
    """
    This function will enable continuous recording through the device, while writing to a buffer
    every segment
    :param mic: SoundFlux object
    :param q: Queue to store captured sound windows
    :return: None
    """
    while not stop_event.is_set()
        l, data = mic.recorder.read()
        qo.put(data)
        qi.task_done()

def extract_features_worker(sample_rate,n_windows=100,n_mels=23,n_fft=2048,fmax=8000, qi, qo, stop_event):
    """
    This function will enable continuous transformation of raw input to transformed features
    :param qi: Queue to get audio samples
    :param qo: Queue to put features
    :return: None
    """
    while not (stop_event.is_set() && qi.empty()):
        samples = qi.get()

        feature_set = []
        if samples.shape[1:]:
            channels = samples.shape[1:][0]
        else:
            channels = 1
            samples = np.expand_dims(samples, axis=1)
        for i in range(channels):
            sample_channel_x = samples[:,i]
            hop_length = round(len(sample_channel_x)/n_windows)
            mel_spectrogram = librosa.feature.melspectrogram(y=sample_channel_x,
                                                        sr=sample_rate,
                                                        n_fft=n_fft,
                                                        hop_length=hop_length,
                                                        n_mels = n_mels,
                                                        fmax = fmax)
            decibel_spec = librosa.logamplitude(mel_spectrogram,ref_power=np.max)
            feature_set.append(decibel_spec)
        feature_set = np.array(feature_set)
        feature_set = np.mean(feature_set,axis=0)[:,:n_windows]
        
        qo.put(feature_set)
        qi.task_done()

def inference_worker(qi, fall_action):
    """
    This function will enable continuous inference on feature sets
    :param qi: Queue to get features
    :param fall_action: action to take if fall detected
    :return: None
    """
    while not (stop_event.is_set() && qi.empty()):
        features = qi.get()
        if isFallInference(features):
            do(fall_action)
        qi.task_done()


if __name__ == '__main__':
    run()
