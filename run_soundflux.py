import queue
import time
from threading import Event, Thread

import numpy as np

import librosa
from accelerometer import Accelerometer
from soundflux import SoundFlux

# Set up some global variables
sound_queue = queue.Queue()
feature_queue = queue.Queue()
stop_event = Event()
fall_action = "text"

def run():
    # Instantiate Objects
    mic = SoundFlux(liveFeed=True)
    acc = Accelerometer()

    run_sound_capture = Thread(target=capture_sound_worker, args=(mic, sound_queue, stop_event,))
    run_feature_extractor = Thread(target=extract_features_worker, args=(sound_queue, feature_queue, stop_event,))
    run_inference = Thread(target=inference_worker, args=(feature_queue, fall_action,))

    threads = {"run_sound_capture":run_sound_capture, "run_feature_extractor":run_feature_extractor, "run_inference":run_inference}

    for worker in threads.keys():
        threads[worker].setDaemon(True)
        threads[worker].start()

    print("Listening and running inference... Press any key to stop.")
    if input:
        stop_event.set()
    print("Pipeline finishing...")
    for worker in threads.keys():
        while threads[worker].is_alive():
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
    while not stop_event.is_set():
        l, data = mic.recorder.read()
        qo.put(data)

def extract_features_worker(qi, qo, stop_event, sample_rate=16000, n_mels=23, n_fft=16, hop_length=8, fmax=8000):
    """
    This function will enable continuous transformation of raw input to transformed features
    :param qi: Queue to get audio samples
    :param qo: Queue to put features
    :return: None
    """
    while not (stop_event.is_set() & qi.empty()):
        sample = qi.get()
        mel_spectrogram = librosa.feature.melspectrogram(y=sample,
                                                        sr=sample_rate,
                                                        n_fft=n_fft,
                                                        hop_length=hop_length,
                                                        n_mels = n_mels,
                                                        fmax = fmax)
        qo.put(mel_spectrogram)
        qi.task_done()

def inference_worker(qi, fall_action):
    """
    This function will enable continuous inference on feature sets
    :param qi: Queue to get features
    :param fall_action: action to take if fall detected
    :return: None
    """
    while not (stop_event.is_set() & qi.empty()):
        features = qi.get()
        #if isFallInference(features):
        #    do(fall_action)
        print(features)
        qi.task_done()


if __name__ == '__main__':
    run()
