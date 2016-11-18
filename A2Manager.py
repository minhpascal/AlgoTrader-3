# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 12:39:27 2016

@author: Administrator
"""

import time
import datetime
import KConnect

EXECUTED = 'EXECUTED'
NEWSIGNAL = 'NEWSIGNAL'
LTP = 'LTP'
LASTUPDATED = 'LASTUPDATED'
NEWPRICE = 'NEWPRICE'
NEWPRICE1 = 'NEWPRICE1'
NEWSTOP = 'NEWSTOP'
NEWBUYSELL = 'NEWBUYSELL'
SLBUYSELL = 'SLBUYSELL'
ISSTOPPEDOUT = 'ISSTOPPEDOUT'
STOPLOSS = 'STOPLOSS'

class AManager:
    m_driver = None
    
    signalFile = file('signals.txt', 'a')
    
    def __init__(self):
        time.sleep(5)
        
    def getSignal(self, scripCode=None):
        signal = {}
        f = open('A2State.txt', 'r')
        state = f.readline().rstrip("\n")
        price = f.readline().rstrip("\n")
        print state
        print price
        f.close()
        token = KConnect.getInstrumentToken(scripCode)
        print token
        data = KConnect.getOHLCData(token)
        channelData = self.getChannelData(data)
        print channelData
       
        if state == "NONE":
            if channelData['LASTCANDLEMAX']> channelData['PCHANNELMAX']:
                state = "LONG"
                price = channelData['PCHANNELMAX']
                if channelData['LASTCANDLEOPEN'] > channelData['PCHANNELMAX']:
                    price = channelData['LASTCANDLEOPEN']
            elif channelData['LASTCANDLEMIN']< channelData['PCHANNELMIN']:
                state = "SHORT"
                price = channelData['PCHANNELMIN']
                if channelData['LASTCANDLEOPEN'] < channelData['PCHANNELMIN']:
                    price = channelData['LASTCANDLEOPEN']
            f = open('A2State.txt', 'w')
            f.write(state + "\n"+ str(price)+"\n" + channelData['LASTCANDLETS'])
            f.close()
            tradesFile = file('Trades.txt', 'a')
            tradesFile.write('\n'+str(datetime.datetime.today())+','+state+','+str(price))
            tradesFile.flush()
            tradesFile.close()
        
        if state == "SHORT":
            if channelData['LASTCANDLEMAX']> channelData['PCHANNELMAX']:
                state = "LONG"
                price = channelData['PCHANNELMAX']
                if channelData['LASTCANDLEOPEN'] > channelData['PCHANNELMAX']:
                    price = channelData['LASTCANDLEOPEN']
                f = open('A2State.txt', 'w')
                f.write(state + "\n"+ str(price)+"\n" + channelData['LASTCANDLETS'])
                f.close()
                tradesFile = file('Trades.txt', 'a')
                tradesFile.write('\n'+str(datetime.datetime.today())+','+state+','+str(price))
                tradesFile.flush()
                tradesFile.close()
        elif state == "LONG":
            if channelData['LASTCANDLEMIN']< channelData['PCHANNELMIN']:
                state = "NONE"
                price = channelData['PCHANNELMIN']
                if channelData['LASTCANDLEOPEN'] < channelData['PCHANNELMIN']:
                    price = channelData['LASTCANDLEOPEN']
                f = open('A2State.txt', 'w')
                f.write(state + "\n"+ str(price)+"\n" + channelData['LASTCANDLETS'])
                f.close()
                tradesFile = file('Trades.txt', 'a')
                tradesFile.write('\n'+str(datetime.datetime.today())+','+state+','+str(price))
                tradesFile.flush()
                tradesFile.close()
                
        if state == "SHORT":
            signal[EXECUTED] = "Sell at " + str(price)
            signal[NEWSIGNAL] = "Buy at "+str(channelData['CHANNELMAX'])
            signal[STOPLOSS] = str(float(price)+65)
            if float(channelData['CHANNELMAX']) <  float(price)+65:
                signal[STOPLOSS] = channelData['CHANNELMAX']
            signal[SLBUYSELL] = "Buy"
        elif state == "LONG":
            signal[EXECUTED] = "Buy at " + str(price)
            signal[NEWSIGNAL] = ""
            signal[STOPLOSS] = str(float(price)-65)
            if float(channelData['CHANNELMIN']) >  float(price)-65:
                signal[STOPLOSS] = channelData['CHANNELMIN']
            signal[SLBUYSELL] = "Sell"
        elif state == "NONE":
            signal[EXECUTED] = ""
            signal[NEWSIGNAL] = "Buy at "+str(channelData['CHANNELMAX']) + " Sell at "+str(channelData['CHANNELMIN'])
            signal[STOPLOSS] = ""
            signal[SLBUYSELL] = ""
        signal[LTP] = channelData['LTP']
        signal["TS"] = channelData['TS']
        
        if signal[NEWSIGNAL]:
            buyAtIndex = signal[NEWSIGNAL].find('Buy at')
            sellAtIndex = signal[NEWSIGNAL].find('Sell at')
            if buyAtIndex >= 0 and sellAtIndex >=0:
                atIndex = signal[NEWSIGNAL].find('at')
                newPrice = signal[NEWSIGNAL][atIndex+3:sellAtIndex]
                newPriceValue = float(newPrice)-0.05
                signal[NEWPRICE] = str(newPriceValue)
                newPrice = signal[NEWSIGNAL][sellAtIndex+8:]
                newPriceValue = float(newPrice)+0.05
                signal[NEWPRICE1] = str(newPriceValue)
                signal[NEWBUYSELL] = "BOTH"
            else:
                atIndex = signal[NEWSIGNAL].find('at')
                buyOrSell = signal[NEWSIGNAL][:atIndex-1]
                if buyOrSell == 'Sell':
                    buyOrSell = 'Sell'
                newPrice = signal[NEWSIGNAL][atIndex+3:]
                newPriceValue = float(newPrice)-0.05
                if buyOrSell == 'Sell':
                    newPriceValue = float(newPrice)+0.05
                newPrice = str ( newPriceValue )    
                signal[NEWPRICE] = newPrice
                signal[NEWBUYSELL] = buyOrSell
        self.signalFile.write(str(channelData)+"\n")
        self.signalFile.write(str(signal)+"\n\n")
        self.signalFile.flush()
        return signal
        
    def getChannelData(self, data):
        channelData = {};
        pChannelMax = -1;
        pChannelMin = 99999;
        prevChannel = data[:12]
        for candle in  prevChannel:
            if candle[2] > pChannelMax:
                pChannelMax = candle[2]
            if candle[3] < pChannelMin:
                pChannelMin = candle[3]
            
        channelMax = -1;
        channelMin = 99999;
        channel = data[1:13]
        for candle in  channel:
            if candle[2] > channelMax:
                channelMax = candle[2]
            if candle[3] < channelMin:
                channelMin = candle[3]
                
        channelData['PCHANNELMAX'] = pChannelMax
        channelData['PCHANNELMIN'] = pChannelMin
        channelData['CHANNELMAX'] = channelMax
        channelData['CHANNELMIN'] = channelMin
        channelData['LASTCANDLEMIN'] = data[-2][3]
        channelData['LASTCANDLEMAX'] = data[-2][2]
        channelData['LASTCANDLEOPEN'] = data[-2][1]
        channelData['LASTCANDLETS'] = data[-2][0]
        channelData['LTP'] = data[-1][4]
        channelData['TS'] = data[-1][0]
        
        return channelData


