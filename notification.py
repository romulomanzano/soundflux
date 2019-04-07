import requests
from config import *
import base64
import datetime
from utils import *

logger = get_generic_logger(__name__)

def register_inference(spectrogram_location, metadata, prediction):
    try:
        idx = 1
        model_prediction = {}
        label = None
        label_proba = 0
        for k, v in prediction.items():
            if k != 'filename':
                model_prediction["class_{}_label".format(idx)] = k
                model_prediction["class_{}_probability".format(idx)] = v
                idx +=1
                if v>label_proba:
                    label = str(k)
                    label_proba = float(v)
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
            "label" : "{} - {}%".format(label, round(label_proba*100,1)),
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
