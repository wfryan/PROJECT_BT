from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from dotenv import load_dotenv
import myLogger as mylog

import os

load_dotenv()
def sendUsgNotif(msg):
    mylog.logInfo(msg)
    account_id = os.getenv("TWILIO_ACCOUNT_SID")
    authToken = os.getenv("TWILIO_AUTH_TOKEN")
    tNum = str(os.getenv("twilNum"))
    adNum = str(os.getenv("adminNum"))
    client = Client(account_id, authToken)
    client.messages.create(
        body =  msg,
        from_ = tNum,
        to=adNum)