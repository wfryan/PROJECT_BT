import smtplib, ssl, os, email
from dotenv import load_dotenv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import platform

load_dotenv()
def sendMail(toaddr, sheetP, sender):
    senderemail = os.getenv("smtpusr")
    body = "Hello there, \n\n Here is the spreadsheet you requested"
    subject = "Budget Spreadsheet - " + sender

    message = MIMEMultipart()
    message["Date"] = str(date.today())
    message["From"] = f"Will Ryan {senderemail}"
    message["To"] = toaddr
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    port = 587
    passw = os.getenv("smtpsw")

    with open(sheetP, "rb") as attatchment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attatchment.read())

    if "Windows" in platform.system():
        splits = sheetP.split("\\")
    else:
        splits = sheetP.split("/")
    temp = splits[len(splits) - 1]
    print(temp)
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", 
        f"attatchment; filename= {temp}",
    )
    message.attach(part)
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(senderemail, passw)
        server.sendmail(senderemail, toaddr, text) 
        #TODO fix email being sent to spam filter

