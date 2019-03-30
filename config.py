"""
General config variables
"""
import alsaaudio
from dotenv import load_dotenv, find_dotenv
import os

# load environment variables
load_dotenv(find_dotenv())


LOG_LEVEL = 'INFO'
MIC_NUMBER_OF_CHANNELS = 4
TARGET_FILE_SAMPLE_WIDTH = 4
MIC_RATE = 16000
MIC_SET_FORMAT = alsaaudio.PCM_FORMAT_S32_LE
MIC_DEVICE = "ac108"
MIC_PERIOD_SIZE = 160
MIC_PERIOD_SIZE_LIVE_FEED = 160
FEED_FILES_FOLDER = os.path.dirname(os.path.realpath(__file__))+"/feed_files/"
FEED_FILES_PREFIX_FORMAT = "%H:%M:%S.%f"
#ACCELEROMETER CONFIGURATIONS
ACC_EARTH_GRAVITY_MS2 = 9.80665
ACC_SCALE_MULTIPLIER = 0.004

ACC_DATA_FORMAT = 0x31
ACC_BW_RATE = 0x2C
ACC_POWER_CTL = 0x2D

ACC_BW_RATE_1600HZ = 0x0F
ACC_BW_RATE_800HZ = 0x0E
ACC_BW_RATE_400HZ = 0x0D
ACC_BW_RATE_200HZ = 0x0C
ACC_BW_RATE_100HZ = 0x0B
ACC_BW_RATE_50HZ = 0x0A
ACC_BW_RATE_25HZ = 0x09

ACC_RANGE_2G = 0x00
ACC_RANGE_4G = 0x01
ACC_RANGE_8G = 0x02
ACC_RANGE_16G = 0x03

ACC_MEASURE = 0x08
ACC_AXES_DATA = 0x32
#ACC Frequency
ACC_FREQUENCY_HZ = 100
#comms setup:
COMMUNICATIONS_DEFAULT_SUPPORT_EMAIL = "hello@soundflux.io"
POSTMARK_DEFAULT_SUPPORT_EMAIL_TOKEN =os.getenv("POSTMARK_DEFAULT_SUPPORT_EMAIL_TOKEN")
POSTMARK_BASE_URL = "https://api.postmarkapp.com/email"
POSTMARK_VENDOR_NAME = "POSTMARK"
TWILIO_VENDOR_NAME = "TWILIO"
TWILIO_ACCT_SID=os.getenv("TWILIO_ACCT_SID")
SOUNDFLUX_SMS_NUMBER = os.getenv("SOUNDFLUX_SMS_NUMBER")
TWILIO_AUTH_TOKEN= os.getenv("TWILIO_AUTH_TOKEN")

#Pipeline Config:
MIN_VOLUME_FOR_INFERENCE = 20

#Device registration
SOUNDFLUX_ACCOUNT_EMAIL=os.getenv("SOUNDFLUX_ACCOUNT_EMAIL")
SOUNDFLUX_SOUNDFLUX_ACCOUNT_TOKEN=os.getenv("SOUNDFLUX_SOUNDFLUX_ACCOUNT_TOKEN")
SOUNDFLUX_DEVICE_ID=os.getenv("SOUNDFLUX_DEVICE_ID")
SOUNDFLUX_MODEL_WEIGHTS_LOCATION = os.getenv("SOUNDFLUX_MODEL_WEIGHTS_LOCATION")
SOUNDFLUX_MODEL_TEST_IMAGE_FOLDER = os.getenv("SOUNDFLUX_MODEL_TEST_IMAGE_FOLDER")
SOUNDFLUX_MODEL_DEFINITION_LOCATION = os.getenv("SOUNDFLUX_MODEL_DEFINITION_LOCATION")
SOUNDFLUX_MODEL_LABELS_MAP_LOCATION = os.getenv("SOUNDFLUX_MODEL_LABELS_MAP_LOCATION")
LIVE_FEED_TARGET_FOLDER = "./feed_files"
LIVE_FEED_INFERENCE_FOLDER = "./feed_files/inference_files"
LIVE_FEED_INFERENCE_ACC_THRESHOLD = 1.1
LIVE_FEED_SPECTROGRAM_WINDOW_SECONDS = 2