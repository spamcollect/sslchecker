#!/usr/bin/python

# Under: GNU GENERAL PUBLIC LICENSE Version 3

# Description: This script should be set up as a daily cronjob.
# By regularly checking if a certificate is still valid, you avoid running your server with expired certificates.
# Feel free to contribute. 

import ssl, socket, time, datetime, smtplib
from email.mime.text import MIMEText

# SMTP settings
SMTP_HOST_SSL = 'smtp.yourdomain.com'
SMTP_USER = 'yoursmtpuser'
SMTP_PASS = 'yourpassword'
SMTP_SENDER_EMAIL = 'donotreply@yourdomain.com'
SMTP_SENDER_PLAIN = 'SSLChecker'

# Recipient emails addresses, comma separated
RECEIVERS = ["you@yourdomain.com"]

# HTTPS hosts to scan
url = ['www.yourdomain.com', 'www.yourdomain2.com']


# iterate thru list
for hostname in url:

    # send SSL request
    ctx = ssl.create_default_context()
    s = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
    # there is no need that your ssl server runs on port 443. If you e.g. want to validdate a imaps connection, change the port here.
    s.connect((hostname, 443))
    cert = s.getpeercert()

    # get certificate expiration date
    valid = cert['notAfter']

    # process string date to date format
    validdate = datetime.datetime.fromtimestamp(int(time.mktime(datetime.datetime.strptime(valid, "%b %d %H:%M:%S %Y %Z").timetuple())))
    # get date from today
    today= datetime.datetime.now()

    # calculate difference between
    difference = (validdate - today).days

    # simple process to alert 30, 14, 3, and 1 day in advance
    if difference is 30 or difference is 14 or difference is 3 or difference is 1:

        # content for the email
        content = "Hello! \n\n" \
                  "the certificate for your domain "+hostname+" is about to expire in "+str(difference)+" days.\n" \
                  "The exact date is: "+str(validdate)+"\n\n" \
                  "Please update the certificate as soon as possible.\n\n" \
                  "Best regards\n" \
                  "Certicate Checkbot - SSLChecker"

        # building message
        msg = MIMEText(content, 'plain')
        msg['Subject'] = "The certificate for "+hostname+" is about to expire in "+str(difference)+" days"
        msg['From'] = SMTP_SENDER_EMAIL

        # send out message
        try:
            smtpObject = smtplib.SMTP_SSL(SMTP_HOST_SSL)
            smtpObject.login(SMTP_USER, SMTP_PASS)
            smtpObject.sendmail(SMTP_SENDER_EMAIL, RECEIVERS, msg.as_string())
            print ("Successfully sent email")
        except smtplib.SMTPException:
            print ("Error: unable to send email")
