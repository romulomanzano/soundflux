import time
from multiprocessing import Process, Queue, Value

import numpy as np

import librosa
from accelerometer import Accelerometer
from soundflux import SoundFlux

# Set up some global variables
sound_queue = Queue()
feature_queue = Queue()
inference_queue = Queue()
fall_action = "text"

def run():
    # Instantiate Objects
    mic = SoundFlux(live_feed=True)
    acc = Accelerometer()
    go = Value('i', 1)

    processes = {
        "data_capturer":
        Process(target=capture_sound_worker, args=(mic, sound_queue, go,)),
        
        "feature_extractor":
        Process(target=extract_features_worker, args=(sound_queue, feature_queue, go,)),
        
        "inference_runner":
        Process(target=inference_worker, args=(feature_queue, inference_queue, go,)),

        "fall_responder":
        Process(target=response_worker, args=(inference_queue, go, fall_action,)),

        "pipeline_stopper":
        Process(target=pipeline_stopper_worker args=(go,))
        }

    for process in processes.keys():
        processes[process].daemon = True
        processes[process].start()

    print("Listening and running inference... Press any key to stop.")
    
    for process in processes.keys():
        processes(process).join()
        
    print("Pipeline complete!")

def capture_sound_worker(mic, qo, go):
    """
    This function will enable continuous recording through the device, while writing to a buffer
    every segment
    :param mic: SoundFlux object
    :param qo: Queue object to store captured sound windows
    :param go: bool run signal from spawning process
    :return: None
    """
    while go:
        l, data = mic.recorder.read()
        array = np.frombuffer(data, dtype = np.dtype('>i4'))
        if np.max(array) > 15: # placeholder for global config used for volume filtering before doing heavy computation
            #@TODO reorganize array into 100x4 array (samples x channels)
            qo.put(array)

def extract_features_worker(qi, qo, go, sample_rate=16000, n_mels=23, n_fft=1, hop_length=8, fmax=8000):
    """
    This function will enable continuous transformation of raw input to transformed features.
    It will return either a single timestep feature array, or a full nd array.
    :param qi: Queue object to get audio samples
    :param qo: Queue object to put features
    :param go: bool run signal from spawning process
    :return: None
    """
    while go:
        while not qi.empty():
            sample = qi.get()
            # if the below call is to return a single spectrogram
            # column (one timestep), then we should overlap the sample parameter...
            # this would be potentially useful in a RNN classifier
            
            # if the below call is returning a full spectrogram for inference,
            # then we should compile enough in the previous worker and put in
            # queue if it meets the volume threshold...
            # this would be more practical for a pure CNN classifier
            mel_spectrogram = librosa.feature.melspectrogram(y=sample,
                                                            sr=sample_rate,
                                                            n_fft=n_fft,
                                                            hop_length=hop_length,
                                                            n_mels = n_mels,
                                                            fmax = fmax)
            qo.put(mel_spectrogram)

def inference_worker(qi, qo, go):
    """
    This function will enable continuous inference on feature sets
    :param qi: Queue object to get features
    :param qo: Queue object to put results
    :param go: bool run signal from spawning process
    :return: None
    """
    n = 0 # debugging code
    
    while go:
        while not qi.empty():
            features = qi.get()
            #if isFallInference(features):
                #qo.put(True)
            #else:
                #qo.put(False)
            n += 1 # debugging code
            msg = "#" + str(n) + " " + str(type(features)) + " " + str(features.shape) # debugging code
            qo.put(msg) # debugging code

def fall_response_worker(qi, go, fall_action):
    """
    This function will enable continuous monitoring and response to the pipeline
    :param qi: Queue object to get features
    :param go: bool run signal from spawning process
    :param fall_action: string to control response
    :return: None
    """
    while go:
        while not qi.empty():
            fall = qi.get()
            print(str(fall))

def pipeline_stopper_worker(go):
    """
    This function will enable stopping the pipeline
    :param go: bool run signal from spawning process
    :return: None
    """
    stop_command = input("Enter any value to stop the pipeline: ")
    go = Value('i', 0)
    print("Pipeline finishing...")

if __name__ == '__main__':
    run()
