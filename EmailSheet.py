import smtplib, ssl, os, email
from dotenv import load_dotenv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()
def sendSheet(toaddr, sheetP):
    senderemail = "insert here"
    body = "Hello there, \n\n Here is the spreadsheet you requested"
    subject = "BUDGETING SPREADSHEET"

    message = MIMEMultipart()
    message["From"] = senderemail
    message["To"] = toaddr
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    port = 465
    passw = os.getenv("smtpsw")

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context) as server:
        server.login("insert email here later", passw) #TODO setup email and password to test tls encrypted smtp server
        #TODO send email from in here

