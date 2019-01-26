"""
Core class to manage audio recordings
"""
from config import *
import timeit
import sys
import wave


class SoundFlux(object):

    def __init__(self):
        self.recorder = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device=MIC_DEVICE)
        self._initialize_recorder()

    def _initialize_recorder(self):
        """Set configurations for the recorder"""
        self.recorder.setchannels(MIC_NUMBER_OF_CHANNELS)
        self.recorder.setrate(MIC_RATE)
        self.recorder.setformat(MIC_SET_FORMAT)
        self.recorder.setperiodsize(MIC_PERIOD_SIZE)

    def record_x_seconds(self,output_file, seconds=4):
        start = timeit.default_timer()
        frames = []
        while (timeit.default_timer() - start) <= seconds:
            # Read data from device
             l, data = self.recorder.read()
             if l:
                frames.append(data)
        #set the metadata for the file
        # Write your new .wav file with built in Python 3 Wave module
        with wave.open(output_file, 'wb') as wave_file:
           wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
           wave_file.setsampwidth(TARGET_FILE_SAMPLE_WIDTH)
           wave_file.setframerate(MIC_RATE)
           wave_file.writeframes(b''.join(frames))


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'record_sample':
        file_name = sys.argv[2]
        flux = SoundFlux()
        flux.record_x_seconds(file_name)
