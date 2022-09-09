# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 14:50:41 2022

@author: docs9
"""

from DataBuffer import DataBuffer
from const import *
from CsvReader import *
from TechnicalAnalysis import atr, sma, atrband
from utility import dic2Arrays, sliceDic, dic2df, splitDic

TYPE_FIX_PRICE = 0
TYPE_OPEN_TIME = 1
TYPE_CLOSE_TIME = 2


class TradePosition:
    def __init__(self, is_long, time, price):
        self.is_long = is_long
        self.open_time = time
        self.open_price = price
        self.is_closed = False
        
    def close(self, time, price):
        self.close_time = time
        self.close_price = price
        self.is_closed = True
        self.profit = self.close_price - self.open_price
        if not self.is_long:
            self.profit *= -1.0
        self.ror = self.profit / self.open_price
        
class TradeOrder:
    def __init__(self, is_long, typ, price):
        self.is_long = is_long
        self.typ = typ
        self.price = price
    
    def update(self, tohlc):
        return None
    
    def simulate(self, tohlc):
        time = tohlc[0]
        opn = tohlc[1]
        high = tohlc[2]
        low = tohlc[3]
        clos = tohlc[4]
        
        if self.is_typ == TYPE_FIX_PRICE:
            if self.is_typ >= low and self.price <= high:
                p = TradePosition(self.is_long, time, self.price)
                return p
        elif self.is_type == TYPE_OPEN_TIME:
            p = TradePosition(self.is_long, time, opn)
            return p
        elif self.is_type == TYPE_CLOSE_TIME:
            p = TradePosition(self.is_long, time, clos)
            return p           
        
        return None
    
class Trade:
    def __init__(self, features: dict, calc_functions: dict, initialData: dict):
        self.orders = []
        self.positions = []
        self.features = features
        self.calc_functions = calc_functions
        buffer = DataBuffer(self.features, self.calc_functions)
        buffer.loadData(initialData)
        self.buffer = buffer
        
# -----

def test():
    dic, length = CsvReader.loadBitflyerCsv('./data/btcjpy_m15s.csv')
    d1, d2 = splitDic(dic, length - 200)
    features = [SMA, ATR, ATR_BAND_LOWER, ATR_BAND_UPPER]
    calc_functions = {SMA: sma, ATR: atr, ATR_BAND_LOWER: atrband, ATR_BAND_UPPER: atrband}
    trade = Trade(features, calc_functions, d1)
    d = trade.buffer.data()
    df = dic2df(d)
    df.to_csv('./data/test.csv', index=False)
        
    
    
if __name__ == '__main__':
    test()