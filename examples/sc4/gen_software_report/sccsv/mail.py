from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders
import smtplib
import os

def send(from_addr, to_addrs, subject, body, filename, host='localhost'):
    # The first part of generating the email is to parse all of the config
    # settings and dump them into the msg object that we have created.
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(str(body)))
    
    # The next stage it to build & attach the file to the email message object.
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(filename, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 
                    'attachment; filename="%s"' % os.path.basename(filename))
    msg.attach(part)
    
    # Lastly, we need to send the email...
    smtp = smtplib.SMTP(host)
    smtp.sendmail(from_addr, to_addrs, msg.as_string())
    smtp.close()