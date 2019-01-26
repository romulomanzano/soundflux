"""
General config variables
"""
import alsaaudio

MIC_NUMBER_OF_CHANNELS = 4
MIC_RATE = 16000
MIC_SET_FORMAT = alsaaudio.PCM_FORMAT_S32_LE
MIC_DEVICE = "ac108"
MIC_PERIOD_SIZE = 160