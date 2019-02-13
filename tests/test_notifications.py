import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from communications import Email, Sms

def test_email(to):
    em = Email()
    em.send_email_new_conversation("Hello from SoundFlux!","<p>This is great!</p>",
                                   [to])

def test_sms(to):
    em = Sms()
    em.send_sms("Hello from SoundFlux!",to)


if __name__ == '__main__':
    type = sys.argv[1]
    to = sys.argv[2]
    if type == "email":
        test_email(to)
    if type == "sms":
        test_sms(to)
