import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

os.environ['TWILIO_ACCOUNT_SID'] = 'ACac1cc8f4fd48669ba8516ea6c3493422'
os.environ['TWILIO_AUTH_TOKEN'] = 'c4a547c5583b10f8fcd680ab7d8a1d76'
os.environ['TWILIO_VERIFY_SERVICE_SID'] = 'VAb4fbe6c9b44a5cc179993018c7e1079b'



client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
verify = client.verify.services(os.environ.get('TWILIO_VERIFY_SERVICE_SID'))


def send(mobile):
    phone = "+91"+ str(mobile)
    verify.verifications.create(to=phone, channel='sms')



def check(mobile, code):
    phone = "+91"+ str(mobile)
    try:
        result = verify.verification_checks.create(to=phone, code=code)
    except TwilioRestException:
        print('no')
        return False
    return result.status == 'approved'
