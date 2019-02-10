"""
Core class to manage audio recordings
"""
from config import *
import timeit
import sys
import wave
import datetime
import constants
import utils

@utils.logged
class SoundFlux(object):
    """
    This will act as a wrapper on the alsaaudio PCM class.
    It may have ore or more PCM attributes (recording and player)
    """

    def __init__(self):
        self.recorder = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device=MIC_DEVICE)
        self._initialize_recorder()

    def _initialize_recorder(self):
        """Set configurations for the recorder"""
        self.recorder.setchannels(MIC_NUMBER_OF_CHANNELS)
        self.recorder.setrate(MIC_RATE)
        self.recorder.setformat(MIC_SET_FORMAT)
        self.recorder.setperiodsize(MIC_PERIOD_SIZE)

    def record_x_seconds(self, seconds=constants.FEED_FILE_LENGTH):
        start = timeit.default_timer()
        frames = []
        while (timeit.default_timer() - start) <= seconds:
            # Read data from device
             l, data = self.recorder.read()
             if l:
                frames.append(data)
        return frames

    def record_and_save_x_seconds(self,output_file, seconds=constants.FEED_FILE_LENGTH):
        frames = self.record_x_seconds(seconds=seconds)
        # Write your new .wav file with built in Python 3 Wave module
        with wave.open(output_file, 'wb') as wave_file:
           wave_file.setnchannels(MIC_NUMBER_OF_CHANNELS)
           wave_file.setsampwidth(seconds)
           wave_file.setframerate(MIC_RATE)
           wave_file.writeframes(b''.join(frames))

    def capture_live_feed(self,output_directory=FEED_FILES_FOLDER,chunk_size=constants.FEED_FILE_LENGTH):
        """
        This function will enable continuous recording through the device, while writing to smaller files
        of x number of seconds
        :param output_directory: Where the files should go, include slash
        :param chunk_size: Number of seconds per file captured
        :return: None
        """
        #TODO: Use threading!
        while True:
            now = datetime.datetime.utcnow()
            file_name = self._generate_feed_filename(now, output_directory,chunk_size=chunk_size)
            self.record_and_save_x_seconds(file_name,seconds=chunk_size)


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'record_sample':
        file_name = sys.argv[2]
        flux = SoundFlux()
        flux.record_and_save_x_seconds(file_name)
    if action == 'capture_live_feed':
        flux = SoundFlux()
        flux.capture_live_feed()
    if action == 'get_live_feeds':
        flux = SoundFlux()
        flux.get_available_feed_files()
