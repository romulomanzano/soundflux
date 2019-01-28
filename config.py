"""
General config variables
"""
import alsaaudio
import os

LOG_LEVEL = 'INFO'
MIC_NUMBER_OF_CHANNELS = 4
TARGET_FILE_SAMPLE_WIDTH = 4
MIC_RATE = 16000
MIC_SET_FORMAT = alsaaudio.PCM_FORMAT_S32_LE
MIC_DEVICE = "ac108"
MIC_PERIOD_SIZE = 160
FEED_FILES_FOLDER = os.path.dirname(os.path.realpath(__file__))+"/feed_files/"
FEED_FILES_PREFIX_FORMAT = "%H:%M:%S.%f"
