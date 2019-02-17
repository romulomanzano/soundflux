import numpy as np
import imageio
import librosa
from config import *
from datetime import datetime as dt
import matplotlib.pyplot as plt

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

def extract_features_worker(qi, qo, go, model_type, save_spectrograms, sample_rate=16000, 
                            n_mels=320, n_fft=2048, hop_length=10, fmax=8000, inference_window=1):
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

        if model_type=="cnn":
            window.put(range(int(samples_in_window/2)), window.take(range(int(samples_in_window/2), samples_in_window))) # move second half of data to beginning then fill the second half with a for loop
            for step in range(int(samples_in_window/(MIC_PERIOD_SIZE_LIVE_FEED*2))):
                if go.value==0 and qi.empty():
                    qo.put(False)
                    return
                
                # compile enough samples to make a complete spectrogram for cnn inference
                window.put(range(int(samples_in_window/2 + step*MIC_PERIOD_SIZE_LIVE_FEED),
                            int(samples_in_window/2 + (step+1)*MIC_PERIOD_SIZE_LIVE_FEED)),
                            qi.get())
                
            if np.max(window) > MIN_VOLUME_FOR_INFERENCE:
                mel_spectrogram = librosa.feature.melspectrogram(y=window,
                                                                sr=sample_rate,
                                                                n_fft=n_fft,
                                                                hop_length=hop_length,
                                                                n_mels=n_mels,
                                                                fmax=fmax)
                
                decibal_spec = librosa.logamplitude(mel_spectrogram, ref_power=np.max)
                qo.put(decibal_spec)
                
                if save_spectrograms:
                    #imageio.imsave("mel_spectrogram_{}.bmp".format(dt.now()), decibal_spec)
                    plt.figure(figsize=(10,4))
                    librosa.display.specshow(decibal_spec, y_axis="log", fmax=8000, x_axis="time", freq_fmt="Hz")
                    plt.savefig("mel_spectrogram_{}.tiff".format(dt.now()))

        if model_type=="rnn":
            if go.value==0 and qi.empty():
                return              
        # librosa call is to return a single spectrogram time step for an RNN classifier

def inference_worker(qi, qo, go):
    """
    This function will enable continuous inference on feature sets
    :param qi: Queue object to get features
    :param qo: Queue object to put results
    :param go: bool run signal from spawning process
    :return: None
    """
    n = 0 # debugging code
    
    while True:
        features = qi.get()
        if type(features) == bool:
            qo.put(False)
            return
        #elif isFallInference(features): @TODO port and call inference code
            #qo.put(True)

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
    while True:
        state_change = qi.get()
        if state_change == False:
            return
        print(str(state_change)) #@TODO call texting/calling functions
