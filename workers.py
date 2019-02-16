import numpy as np

import librosa


def capture_sound_worker(mic, qo, go):
    """
    This function will enable continuous recording through the device, while writing to a buffer
    every segment
    :param mic: SoundFlux object
    :param qo: Queue object to store captured sound windows
    :param go: bool run signal from spawning process
    :return: None
    """
    while go.value==1:
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
    while go.value==1:
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
    
    while go.value==1:
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
    while go.value==1:
        while not qi.empty():
            fall = qi.get()
            print(str(fall))
