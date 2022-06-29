from flask import Flask, current_app, request, redirect, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.twiml.messaging_response import MessagingResponse
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from dotenv import load_dotenv
from dataEntryScript import handleData
from dataEntryScript import formatMsg
from dataEntryScript import genOverview

import os

load_dotenv()
PORT_env = os.getenv("port")
app = Flask(__name__)
auth = HTTPBasicAuth()
users = {
    str(os.getenv("usname")):generate_password_hash(os.getenv("pss"))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
    sendUsgNotif("Message sent: Code 401")

def validate_t_request(f):
    @wraps(f)
    def decorated_fn(*args, **kwargs):
        validator = RequestValidator(os.getenv('TWILIO_AUTH_TOKEN'))

        valid_req = validator.validate(request.url, request.form, request.headers.get('X-TWILIO-SIGNATURE', ''))
        if valid_req or current_app.debug:
            return f(*args, **kwargs)
        else:
            return abort(403)

    return decorated_fn

def sendUsgNotif(msg):
    account_id = os.getenv("TWILIO_ACCOUNT_SID")
    authToken = os.getenv("TWILIO_AUTH_TOKEN")
    tNum = str(os.getenv("twilNum"))
    adNum = str(os.getenv("adminNum"))
    client = Client(account_id, authToken)
    client.messages.create(
        body =  msg,
        from_ = tNum,
        to=adNum)


@app.route("/sms", methods=['GET', 'POST'])
@validate_t_request
@auth.login_required
def sms_reply():

    msg = request.values.get('Body', None)
    sender = request.values.get('From', None)
    resp = MessagingResponse()
    if "|" in msg:
        handleData(msg, sender)
        body = formatMsg(sender)
    elif "Overview" in msg:
        body = genOverview(sender)
    else:
        body = "Last Purchase: \n" + formatMsg(sender)
    resp.message(body)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = PORT_env)

