'''
Created on Oct 20, 2016

@author: apte
'''
from selenium import webdriver
from kiteconnect import KiteConnect
from urlparse import urlparse, parse_qs
import Constants
import time
import requests.packages
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

kite = KiteConnect(api_key=Constants.API_KEY)
login_data  = None

def login():
    m_attempt = 0
    try:
        url = kite.login_url()
        driver = webdriver.Chrome()
        driver.get(url)
        
        
        driver.find_element_by_xpath('//*[@id="inputone"]').send_keys(Constants.USER1_ID)
        driver.find_element_by_xpath('//*[@id="inputtwo"]').send_keys(Constants.USER1_LP)
        driver.find_element_by_xpath('//*[@id="loginform"]/div[1]/div[1]/button').click()
        
        
        driver.find_element_by_xpath('//*[@id="twofaform"]/div[1]/input').send_keys(Constants.TWOFAANSWER)
        driver.find_element_by_xpath('//*[@id="twofaform"]/div[2]/input').send_keys(Constants.TWOFAANSWER)
        driver.find_element_by_xpath('//*[@id="twofaform"]/div[3]/div[1]/button').click()
        
        current_url = ""
        timeOutIndex = 0
        while current_url.find("success") < 0 and timeOutIndex < 5:
            time.sleep(1)
            current_url = driver.current_url
            timeOutIndex = timeOutIndex+1
            
        driver.close();
        
        print current_url
        parsedUrl = urlparse(current_url)
        print parsedUrl
        queryData = parsedUrl[4]
        print queryData
        parsedQuery = parse_qs(queryData)
         
        request_token = parsedQuery['request_token'][0]
        
        # request_token = "5mnynoizo9n0a2skil3aewj0ouug5ya2" 
        # 
        data = kite.request_access_token(request_token, secret=Constants.SECRET_KET)
        kite.set_access_token(data["access_token"])
        return data
    except:
        print "Exception while logging in. Tring to login again"
        m_attempt = m_attempt +1
        if m_attempt <= 2:
            return login()
        else :
            print "Max Login attemp exceeded"

def getInstrumentToken(tradingSymbol):
    instruments = kite.instruments("NFO")
    for instrument in instruments:
        if instrument['tradingsymbol'] == tradingSymbol:
            return instrument['instrument_token'];
        
def getIndexToken(tradingSymbol):
    instruments = kite.instruments("NSE")
    for instrument in instruments:
        if instrument['tradingsymbol'] == tradingSymbol:
            return instrument['instrument_token'];
        
def getHistoricalData(intrumentToken, fromDate, toDate, interval):
    historical = kite._get("market.historical", {
            "instrument_token": intrumentToken,
            "from": fromDate,
            "to": toDate,
            "interval": interval,
            "public_token":login_data['public_token'],
            "user_id":Constants.USER1_ID}
                )
    return historical

def getLTP(intrumentToken):
    currentDate = str(datetime.datetime.today()).split()[0]
    historical = kite._get("market.historical", {
            "instrument_token": intrumentToken,
            "from": currentDate,
            "to": currentDate,
            "interval": '5minute',
            "public_token":login_data['public_token'],
            "user_id":Constants.USER1_ID}
                )
    candles_data = historical['candles']
    ltp = candles_data[-1][4]
    return ltp

def getOHLCData(token):
    currentDate = str(datetime.datetime.today()).split()[0]
    prevDate = str(datetime.datetime.now()-datetime.timedelta(5)).split()[0]
#         urlString = "https://api.kite.trade/instruments/historical/"+str(token)+"/15minute?public_token=72eadee8f14f5a9da3a3082192bf0585&user_id=DA0522&api_key=kitefront&from="+prevDate+"&to="+currentDate
#         response = requests.get(url = urlString, headers=headers_data)
#         result = response.json()
    candles = getHistoricalData(token, prevDate, currentDate, '15minute')['candles']
    candles_data = candles[-28:]
    #print candles_data
    newData = []
    prevCandle = None
    for candle in candles_data:
        if candle[0].find("09:15:00") > -1:
            newCandle = candle
            newData.append(newCandle)
        elif prevCandle != None and prevCandle[0].find(":00:00") > -1 and candle[0].find(":15:00"):
            newCandle = [None]*5
            newCandle[0] = prevCandle[0]
            newCandle[1] = prevCandle[1]
            if prevCandle[2] >  candle[2]:
                newCandle[2] = prevCandle[2] 
            else:
                newCandle[2] = candle[2]
            if prevCandle[3] <  candle[3]:
                newCandle[3] = prevCandle[3] 
            else:
                newCandle[3] = candle[3]
            newCandle[4] = candle[4]
            newData.append(newCandle)
        elif prevCandle != None and prevCandle[0].find(":30:00") > -1 and candle[0].find(":45:00"):
            newCandle = [None]*5
            newCandle[0] = prevCandle[0]
            newCandle[1] = prevCandle[1]
            if prevCandle[2] >  candle[2]:
                newCandle[2] = prevCandle[2] 
            else:
                newCandle[2] = candle[2]
            if prevCandle[3] <  candle[3]:
                newCandle[3] = prevCandle[3] 
            else:
                newCandle[3] = candle[3]
            newCandle[4] = candle[4]
            newData.append(newCandle) 
        prevCandle = candle
    newData.append(candles_data[-1])
    return newData

login_data = login()
# token = getInstrumentToken("NIFTY16OCTFUT")
# historical = getHistoricalData(token, '2016-10-25', '2016-10-25', 'minute', login_data['public_token'])
# print historical