# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 12:30:07 2016

@author: Administrator
"""

import time
import Constants
import EmailManager
import A2Manager
from A2Manager import AManager
import SMSManager
from ZerodhaManager import ZerodhaManager
import thread
import threading
import sys
from datetime import datetime
from KCZerodhaManager import KCZerodhaManager

class A2Trader:
    zm1 = None
    scrip_name = 'NIFTY16NOVFUT'
    f = file('Log.txt', 'w')
    a2Manager = None
     
    def __init__(self):
        self.zm1 = KCZerodhaManager()
        self.a2Manager = AManager()
        sys.stdout = self.f
        
    def processSignal(self, isFirstTrade):
        
        signal = self.a2Manager.getSignal(self.scrip_name)
        #banksignal = self.s2Manager.getBankNiftySignal()
        
        text = ""
        text = text + "Executed Signal  " + signal[A2Manager.EXECUTED] + "\n"
        text = text + "New Signal       " + signal[A2Manager.NEWSIGNAL] + "\n"
        text = text + "LTP             " + str(signal[A2Manager.LTP]) + "\n"
        text = text + "STOPLOSS             " + str(signal[A2Manager.STOPLOSS]) + "\n"
        SMSManager.sendSMS(text, "+919823856761")
        
        #executedSignal = "Sell Stopped Out"
        #stopLossString = "17140.81"
        #newSignal = "Buy at 7800.75 Stop 7750.92 "
        t2 = threading.Thread(target=self.processOrder, args=(self.zm1,signal,150,self.scrip_name,"DA0522"))
        t2.start()
        
        print "Order Processing Thread Complete"
        self.f.flush()
        
    def processOrder(self, zmgr ,signal, quantity, scripCode, userName):
        print signal
        isMIS = False
        openQuantity = zmgr.getNetPositionAPI(scripCode)
        print openQuantity
        newOrderQuantity = quantity
        if openQuantity != 0:
            newOrderQuantity = quantity*2
        
        zmgr.cancelAllOrdersAPI(scripCode)
        time.sleep(2)
        if openQuantity == 0 and signal[A2Manager.EXECUTED].find('Buy') > -1:
            zmgr.placeAPIOrder(scripCode, quantity, 'Buy', isMIS, 'MARKET')
        elif openQuantity == 0 and signal[A2Manager.EXECUTED].find('Sell')> -1:
            zmgr.placeAPIOrder(scripCode, quantity, 'Sell', isMIS, 'MARKET')
        
        time.sleep(1)
        openQuantity = zmgr.getNetPositionAPI(scripCode)
            
        if signal[A2Manager.NEWSIGNAL]:
            if openQuantity == 0:
                if signal[A2Manager.NEWBUYSELL] == "BOTH":
                    zmgr.placeAPIOrder(scripCode, quantity, "Buy", isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE]))
                    zmgr.placeAPIOrder(scripCode, quantity, "Sell", isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE1]))
                else:
                    zmgr.placeAPIOrder(scripCode, quantity, signal[A2Manager.NEWBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE]))
            elif signal[A2Manager.NEWBUYSELL] == "Buy":
                if float(signal[A2Manager.STOPLOSS]) < float(signal[A2Manager.NEWPRICE]):
                    zmgr.placeAPIOrder(scripCode, quantity, signal[A2Manager.SLBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.STOPLOSS]))
                    zmgr.placeAPIOrder(scripCode, quantity, signal[A2Manager.NEWBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE]))
                else:
                    zmgr.placeAPIOrder(scripCode, newOrderQuantity, signal[A2Manager.NEWBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE]))
            else:
                if float(signal[A2Manager.STOPLOSS]) > float(signal[A2Manager.NEWPRICE]):
                    zmgr.placeAPIOrder(scripCode, quantity, signal[A2Manager.SLBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.STOPLOSS]))
                    zmgr.placeAPIOrder(scripCode, quantity, signal[A2Manager.NEWBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE]))
                else:
                    zmgr.placeAPIOrder(scripCode, newOrderQuantity, signal[A2Manager.NEWBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.NEWPRICE]))
        else:
            if openQuantity != 0:
                zmgr.placeAPIOrder(scripCode, quantity, signal[A2Manager.SLBUYSELL], isMIS, 'SL-M', float(signal[A2Manager.STOPLOSS]))
                        
        text = userName + " -  Order Processing Complete"
        SMSManager.sendSMS(text, "+919823856761")
        self.f.flush()
            
        
    def startTrading(self):
        
        while True:
            currentMinute = datetime.now().minute
            currentHour = datetime.now().hour
            firstTrade = (currentHour == 9 and currentMinute == 16)
            nthTrade = (  currentHour <= 15 and (currentHour >= 9 and currentMinute == 31) or (currentMinute == 01 and currentHour > 9) ) 
            niftyTradingDone = ( currentHour == 15 and currentMinute >= 29) or currentHour >=16
                
            #print "Processing - " + str(currentHour) + ":" + str(currentMinute)
            if niftyTradingDone:
                break
            elif firstTrade or nthTrade :
                print "Processing - " + str(currentHour) + ":" + str(currentMinute)
                self.f.flush()
                #self.processSignal(firstTrade)
                thread.start_new_thread(self.processSignal, (firstTrade,))
            time.sleep(60)
        
        #self.zm.openFunds()
        self.zm.printScreen('Funds.png')
        EmailManager.sendMailWithAttachments(['Funds.png'], "Trading Done", "Trading done for the day", ['apte.amit@yahoo.com','aniruddha.patwardhan@gmail.com'])
        self.f.close()
        sys.exit()
        #self.zm1.close()
        #self.a2Manager.close()
        
weekday = datetime.today().weekday()
print "weekday is"
print str(weekday)
if weekday == 5 or weekday == 6:
    EmailManager.sendTextMail("Its a trading holiday", "AutoTrader not"+str(weekday)+" started today", ['apteag@gmail.com'])
    SMSManager.sendSMS("Its a trading holiday", "9823856761")
else :
    tradeManager = A2Trader()
    tradeManager.startTrading()
