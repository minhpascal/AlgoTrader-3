# -*- coding: utf-8 -*-
"""
Created on Sun May 15 11:06:06 2016

@author: Amit
"""

#!/usr/bin/python
 
import urllib2
import cookielib
import sys
import Constants
import boto3
import EmailManager

def sendSMS(smsText, mobileNumber):
    client = boto3.client(
        'sns',
        aws_access_key_id="AKIAJXC7SFUDJFCW5PKA",
        aws_secret_access_key="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",
        region_name='us-east-1'
    )

    #client.publish(PhoneNumber="+919823856761", Message=smsText, Subject='Trade V Update')
    EmailManager.sendTextMail("Trade Update", smsText, 'apteag@gmail.com')
    
    print "SMS has been sent."

def sendW2SMS(smsText, mobileNumber):
    username = Constants.W2S_ID
    passwd = Constants.W2S_PW
    message = smsText
    number = mobileNumber
    message = "+".join(message.split(' '))
     
    #Logging into the SMS Site
    url = 'http://site24.way2sms.com/Login1.action?'
    data = 'username='+username+'&password='+passwd+'&Submit=Sign+in'
     
    #For Cookies:
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
     
    # Adding Header detail:
    opener.addheaders = [('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36')]
     
    try:
        opener.open(url, data)
    except IOError:
        print "Error while logging in."
        sys.exit(1)
     
     
    jession_id = str(cj).split('~')[1].split(' ')[0]
    send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
    send_sms_data = 'ssaction=ss&Token='+jession_id+'&mobile='+number+'&message='+message+'&msgLen=136'
    opener.addheaders = [('Referer', 'http://site25.way2sms.com/sendSMS?Token='+jession_id)]
     
    try:
        opener.open(send_sms_url,send_sms_data)
    except IOError:
        print "Error while sending message"
        
    
    print "SMS has been sent."
    

