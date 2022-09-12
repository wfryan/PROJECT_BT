from hashlib import sha1
from flask import Flask, current_app, request, redirect, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.twiml.messaging_response import MessagingResponse
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from dotenv import load_dotenv
import hashlib
from dataEntryScript import changeDateJson, checkAuthUser, formatMsgJson, genOverviewJson, handleDataFromJson
from dataEntryScript import initJsonAccount, jsonIfy, manualOverJson, sendSheetJson, setupSumJson
from dataEntryScript import turnOver
import os, threading, time
import schedule

load_dotenv()

#handles the autmoatic cycledate turnover
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

#security stuff. could be improved upon
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
    #print(request.values.get('From', None))

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
    sender = hashlib.sha256(request.values.get('From', None).encode('utf-8')).hexdigest()
    resp = MessagingResponse()
    #print(hash(sender[1:]))
    #Here is where the message gets parsed and the data gets handled and sent where it needs to be
    if "|" in msg and "Init" not in msg:
        #Handles a purchase
        handleDataFromJson(msg, sender)
        body = formatMsgJson(sender)
    elif "Overview" in msg:
        #handles overview
        body = genOverviewJson(sender)
    elif "Init" in msg and len(msg) < 6:
        #INIT HANDLING, wrong format
        body = "Incorrect Format\n Correct Format: Init : File Name : Billing Date : Budget "
    elif "Init"  in msg:
        #INIT HANDLING, proper format
        temp = msg.split(":")
        body = initJsonAccount(request.values.get('From', None), temp[1][1:], temp[2][1:], temp[3][1:])
    elif "Change Date" in msg.title():
        #Changes cycle date.
        if len(msg) > 14:
            temp = msg.split(" ")
            newDate = temp[len(temp)-1]
            changeDateJson(newDate, sender)
            body = "Budget Date Changed to: " + newDate
        else:
            body = "Incorrect Format: Use \"Change Date MM/DD/YY\" "
    elif "Refresh" in msg.title():
        #Refreshes sum of total spent
        setupSumJson(sender)
        body = "Total spent recalculated: call overview to get an updated value"
    elif "Email" in msg and "@" in msg:
        #Emails the sheet
        splits = msg.split(" ")
        addr = ""
        for i in range(len(splits)):
            if "@" in splits[i]:
                addr = splits[i]

        body = sendSheetJson(addr, sender)
    elif "JSON" in msg:
        #Jsonifys a preexisting account!
        splits = msg.split(":")
        jsonIfy(request.values.get('From', None)[2:], sender, splits[1])
        body = formatMsgJson(sender) + "\n\n" + genOverviewJson(sender)
    elif "Manual Override" in msg:
        #Manual override for cycle date. should be a server side admin command based on its sole usecase
        if os.getenv("overrideCode") in msg:
            manualOverJson(sender)
            body = "Cycle override successful"
        else:
            body = "Contact Administrator"
    else:
        #Defaults to last purchase as a response because this assumes the text came from an authorized user
        # should switch into a conditional check
        # sending last purchase or a program overview dependent on whether or not the user is authorized
        #TODO make this conditional
        if checkAuthUser(sender):
            app.logger.warning("Message Sent from Authorized Number")
            body = "Last Purchase: \n" + formatMsgJson(sender)
        else:
            app.logger.warning("Message sent: Unauthorized Number. Prompting to init account")
            body = "Want to signup? Text back Init followed by a filename, billing date (just the day), and your budget cap!\n"
            body+= "The format should be Init : your filename : your billing day : your budget cap\n"
            body+= "\nBilling day should just be the day. So if your billing cycle ends on the 21st of the month, just say 21\n"
            body+= "Same thing or your budget cap! If your budget is 500 USD, just send 500! The currency doesn't matter!\n"
        
    resp.message(body)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = PORT_env, debug=True)
