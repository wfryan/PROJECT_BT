from hashlib import sha1
from flask import Flask, current_app, request, redirect, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.twiml.messaging_response import MessagingResponse
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from dotenv import load_dotenv
from sendMsgs import sendUsgNotif
from dataEntryScript import handleData, handleTurn, initNewAccount
from dataEntryScript import formatMsg, setupSum, turnOver, manualOverride
from dataEntryScript import genOverview, sendSheet, changeDate
import os, threading, time
import schedule
import myLogger as mylog


load_dotenv()

def updateCycle():
    while True:
        schedule.run_pending()
        time.sleep(15)

schedule.every().day.at("03:15").do(turnOver)
cycleThread = threading.Thread(target=updateCycle)
cycleThread.start()

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
    #print(request.values.get('From', None))
    if request.values.get('From', None) in os.getenv("authNumbers"):
        mylog.logInfo("Message Sent from Authorized Number")
    else:
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


@app.route("/sms", methods=['GET', 'POST'])
@validate_t_request
@auth.login_required
def sms_reply():
    msg = request.values.get('Body', None)
    sender = request.values.get('From', None)
    resp = MessagingResponse()
    if "|" in msg and "Init" not in msg:
        handleData(msg, sender)
        body = formatMsg(sender)
    elif "Overview" in msg:
        body = genOverview(sender)
    elif "Init" in msg and len(msg) < 6:
        body = "Incorrect Format\n Correct Format: Init : Billing Date : Budget "
    elif "Init"  in msg:
        temp = msg.split(":")
        body = initNewAccount(sender, temp[1][1:], temp[2][1:])
    elif "Change Date" in msg.title():
        if len(msg) > 14:
            temp = msg.split(" ")
            newDate = temp[len(temp)-1]
            changeDate(newDate, sender)
            body = "Budget Date Changed to: " + newDate
        else:
            body = "Incorrect Format: Use \"Change Date MM/DD/YY\" "
    elif "Refresh" in msg.title():
        setupSum(sender)
        body = "Total spent recalculated: call overview to get an updated value"
    elif "Email" in msg and "@" in msg:
        splits = msg.split(" ")
        addr = ""
        for i in range(len(splits)):
            if "@" in splits[i]:
                addr = splits[i]

        body = sendSheet(addr, sender)
    elif "Manual Override" in msg:
        if os.getenv("overrideCode") in msg:
            manualOverride(sender)
            body = "Cycle override successful"
        else:
            body = "Contact Administrator"
    else:
        body = "Last Purchase: \n" + formatMsg(sender)
    resp.message(body)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = PORT_env, debug=True)
