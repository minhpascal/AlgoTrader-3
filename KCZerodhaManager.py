'''
Created on Oct 27, 2016

@author: Administrator
'''
from KConnect import kite

class KCZerodhaManager:
    
    def __init__(self):
        pass

    def getNetPositionAPI(self, scripCode, product = 'NRML'):
        positions =  kite.positions()['net']
        for position in positions:
            if position['tradingsymbol'] == scripCode and position['product'] == product:
                return position['quantity']
        return 0

    def cancelAllOrdersAPI(self, scripCode, variety='regular'):
        orders = kite.orders()
        for order in orders:
            if order['tradingsymbol'] == scripCode:
                order_status = order['status']
                if "CANCELLED" in order_status or "REJECTED" in order_status or "COMPLETE" in order_status:
                    pass
                else:
                    print order
                    kite.order_cancel(order['order_id'],variety)
    
    def placeAPIOrder(self, scrip_name, quantity, buySell, isMIS, orderType , triggerPrice= None, isAMO = False ):
        if buySell == "Buy":
            buySell = "BUY"
        elif buySell == "Sell":
            buySell = "SELL"
            
        variety = "regular"
        if isAMO:
            variety = "amo"
                
        product = "NRML"
        if isMIS:
            product = "MIS"
            
        kite.order_place('NFO', scrip_name, buySell, quantity, 0, product, orderType, "DAY", 0, triggerPrice, 0, 0, 0, variety)
    
