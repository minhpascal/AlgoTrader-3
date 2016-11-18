from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import Constants


def sendMail(fileName1, fileName2, buySell):
    img_data1 = open(fileName1, 'rb').read()
    img_data2 = open(fileName2, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = buySell +' Order Placed '
    text = MIMEText("Attached Order placing images")
    msg.attach(text)
    image1 = MIMEImage(img_data1, name=os.path.basename(fileName1))
    image2 = MIMEImage(img_data2, name=os.path.basename(fileName2))
    msg.attach(image1)
    msg.attach(image2)
    # SMTP server
    server=smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(Constants.GMAIL_ID,Constants.GMAIL_PW)
    server.sendmail("traderaga@gmail.com", 'apte.amit@yahoo.com', msg.as_string())
    server.quit()
    
def sendMailWithAttachments(fileNameList, subject, message, recipient):
    msg = MIMEMultipart()
    for fileName in fileNameList:
        print fileName
        img_data = open(fileName, 'rb').read()
        image = MIMEImage(img_data, name=os.path.basename(fileName))
        msg.attach(image)
        
    msg['Subject'] = subject
    text = MIMEText(message)
    msg.attach(text)
    # SMTP server
    server=smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(Constants.GMAIL_ID,Constants.GMAIL_PW)
    server.sendmail("traderaga@gmail.com", 'apte.amit@yahoo.com', msg.as_string())
    server.quit()
    
    
def sendTextMail(subject, message, recipient):
    msg = MIMEText(message)
    msg['Subject'] = subject
    # SMTP server
    server=smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(Constants.GMAIL_ID,Constants.GMAIL_PW)
    server.sendmail("traderaga@gmail.com", recipient, msg.as_string())
    server.quit()
    
#sendTextMail("AutoTrader Warning", "Trade V page refrsh failed", ['apteag@gmail.com', 'apte.amit@yahoo.com'])
#sendMailWithAttachments(['Funds.png'], "Trading Done", "Trading done for the day", ['apte.amit@yahoo.com'])