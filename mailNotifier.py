import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mailConfig import mailToNotify
from mailConfig import mailWhoSendNotification
from mailConfig import passwordMail
from mailConfig import smtpServer
from mailConfig import portMailServer


def send_mail(subject, message):
    msg = MIMEMultipart()
    msg['From'] = mailWhoSendNotification
    msg['To'] = mailToNotify
    msg['Subject'] = subject
    msg.attach(MIMEText(message))
    mailserver = smtplib.SMTP(smtpServer, portMailServer)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login(mailWhoSendNotification, passwordMail)
    mailserver.sendmail(mailWhoSendNotification, mailToNotify,
                        msg.as_string())
    mailserver.quit()
