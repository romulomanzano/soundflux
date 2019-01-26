from python_speech_features import mfcc
import scipy.io.wavfile as wav
import timeit
import sys

def test_time_load(file_name='/home/pi/github/falldetection/tests/wav/hello.wav'):
    start = timeit.default_timer()
    #loading
    (rate,sig) = wav.read(file_name)
    mfcc_feat = mfcc(sig,rate)
    print(mfcc_feat[1:3,:])
    #time
    stop = timeit.default_timer()
    print('Time with pythonspeech ', stop - start)
    #less than a second
    assert stop - start < 1

if __name__ == '__main__':
    arg = sys.argv[1]
    test_time_load(arg)
