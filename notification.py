import requests
from config import *
import base64
import datetime
from utils import *

logger = get_generic_logger(__name__)

def register_inference(spectrogram_location, metadata, model_prediction):
    try:
        #Upload to Target
        binary_data = open(spectrogram_location, 'rb').read()
        base64_bytes = base64.b64encode(binary_data)
        bstring = base64_bytes.decode('utf-8')
        order_by_field = datetime.datetime.strptime(metadata['timestamp'], "%m/%d/%Y, %H:%M:%S").timestamp()
        request_data = {
            "sample_details" : {
            "metadata" : {
                "timestamp" : metadata['timestamp'],
                "time_order_desc" : -order_by_field
            },
            "sample_type" : "realtime_inference",
            "model_prediction" : model_prediction,
            "spectrogram" : bstring
            },
            "device_id" : SOUNDFLUX_DEVICE_ID
        }
        url = "https://api.soundflux.io/api/sample/register"
        headers = {'Content-Type': 'application/json',
        'Authorization': "Bearer " + SOUNDFLUX_SOUNDFLUX_ACCOUNT_TOKEN,
        'Email' : SOUNDFLUX_ACCOUNT_EMAIL}
        r = requests.post(url, json=request_data, headers=headers)
        logger.info("{} - {}".format(r.status_code, r.text))
    except Exception as e:
        logger.error("Error {}".format(e))