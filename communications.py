"""
API to interact with email services (Postmark)
"""
from config import *
import requests
import utils
from twilio.rest import Client

@utils.logged
class Email(object):

    def __init__(self, email_vendor=POSTMARK_VENDOR_NAME,
                 retry_if_rate_limit=True):
        self.vendor = email_vendor
        self.retry_if_rate_limit = retry_if_rate_limit

    def send_email_new_conversation(self, subject, message, to,
                                    channel=POSTMARK_DEFAULT_SUPPORT_EMAIL_TOKEN,
                                    internal_id=None):
        # correct for spaces in the 'to' field
        if self.vendor == POSTMARK_VENDOR_NAME:
            send_to = ",".join([t.strip() for t in to])
            data = {'subject': subject, 'htmlbody': message, 'to': send_to,
                    'from': COMMUNICATIONS_DEFAULT_SUPPORT_EMAIL, "TrackOpens": True,
                    'metadata': {'leif_notification_id': internal_id}}
            r = self._send_email_postmark(data, channel)
            return r

    def _send_email_postmark(self, data, channel=POSTMARK_DEFAULT_SUPPORT_EMAIL_TOKEN):
        url = POSTMARK_BASE_URL
        headers = {'Accept': 'application/json', 'X-Postmark-Server-Token': channel}
        try:
            r = requests.post(url, json=data, headers=headers)
            # 200 is the expected return code by definition
            valid = (r.status_code == 200)
            if not valid:
                self.logger.error('Response not valid: {} - {} '.format(r.status_code, r.json()))
            return (r.json(), valid)
        except Exception as e:
            self.logger.error("Message creation failed in postmark: {}".format(str(e)))
            return ({'error': e}, False)

@utils.logged
class Sms(object):
    def __init__(self,vendor = TWILIO_VENDOR_NAME):
        self.vendor = vendor

    def send_sms(self,message,to):
        if self.vendor == TWILIO_VENDOR_NAME:
            self._send_sms_twilio(message,to)

    def _send_sms_twilio(self,message,to):
        # Your Account Sid and Auth Token from twilio.com/console
        account_sid = TWILIO_ACCT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
            body=message,
            from_=SOUNDFLUX_SMS_NUMBER,
            to=to
        )

