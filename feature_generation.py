import numpy as np
import librosa

def extract_spectrogram(samples,sample_rate,n_mels=128,n_fft=2048):
    feature_set = []
    if samples.shape[1:]:
        channels = samples.shape[1:][0]
    else:
        channels = 1
        samples = np.expand_dims(samples, axis=1)
    for i in range(channels):
        sample_channel_x = samples[:,i]
        mel_spectrogram = librosa.feature.melspectrogram(y=sample_channel_x,
                                                     sr=sample_rate,
                                                     n_fft=n_fft,
                                                     n_mels = n_mels
                                                        )
        decibel_spec = librosa.logamplitude(mel_spectrogram,ref_power=np.max)
        feature_set.append(decibel_spec)
    feature_set = np.array(feature_set)
    feature_set = np.mean(feature_set,axis=0)
    return feature_set