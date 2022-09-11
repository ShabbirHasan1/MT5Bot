# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 21:12:55 2022

@author: docs9
"""

import numpy as np
from const import *
from utility import sliceDic
from MathArray import MathArray

def nans(length):
    out = []
    for i in range(length):
        out.append(np.nan)
    return out

class TechnicalAnalysis:
    
    @classmethod 
    def hl2(cls, dic):
        high = dic[HIGH]
        low = dic[LOW]
        out = MathArray.addArray(high, low)
        out = MathArray.multiply(out, 0.5)
        return out
    
    @classmethod
    def sma(cls, array, window):
        n = len(array)
        out = nans(n)
        for i in range(window - 1, n):
            s = 0.0
            count = 0
            for j in range(window):
                a = array[i - j]
                if np.isnan(a):
                    continue
                else:
                    count += 1
                    s += a
            if count > 0:                
                out[i] = s / count
        return out            

    @classmethod            
    def tr(cls, dic):
        high = dic[HIGH]
        low = dic[LOW]
        close = dic[CLOSE]
        
        n = len(close)
        out = nans(n)
        out[0] = high[0] - low[0]
        for i in range(1, n):
            r1 = np.abs(high[i] - low[i])
            r2 = np.abs(high[i] - close[i - 1])
            r3 = np.abs(close[i - 1] - low[i])
            out[i] = np.max([r1, r2, r3])
        return out
       
    @classmethod
    def atr(cls, dic, window):
        trdata = cls.tr(dic)
        out = cls.sma(trdata, window)
        return (out, trdata)
    
    @classmethod
    def atrBand(cls, dic, k):
        atr = dic[ATR]
        inp = dic[CLOSE]
        m =  MathArray.multiply(atr, k)
        upper = MathArray.addArray(inp, m)
        lower = MathArray.subtractArray(inp, m)
        return (upper, lower)
    
# -----
def sequence(key: str, dic: dict, begin: int, end:int, params: dict):
    n = len(dic[OPEN])
    if WINDOW in params.keys():
        window = params[WINDOW]
    else:
        window = 0
        
    if not key in dic.keys():
        data = dic
        begin = 0
        end = n - 1
    else:
        if window > 0:
            if begin < window:
                data = dic
            else:
                data = sliceDic(dic, begin - window, end)
        else:
            data = sliceDic(dic, begin, end)
        
    if key == SMA:
        array = TechnicalAnalysis.sma(data[CLOSE], window)
    elif key == ATR:
        array, _ = TechnicalAnalysis.atr(data, window)
    elif key == ATR_BAND_UPPER or key == ATR_BAND_LOWER:
        k = params[COEFF]
        upper, lower = TechnicalAnalysis.atrBand(data, k)
        if key == ATR_BAND_UPPER:
            array = upper
        else:
            array = lower
    else:
        return False
    
    j = len(array) - (end - begin + 1)
    a = array[j:]
    if key in dic.keys():
        original = dic[key]
        original[begin: end + 1] = a
    else:
        dic[key] = array
    return True

def sma(key, dic, begin, end):
    params = {WINDOW: 14}
    return sequence(key, dic, begin, end, params)

def atr(key, dic, begin, end):
    params = {WINDOW: 14}
    return sequence(key, dic, begin, end, params)

    
def atrband(key, dic, begin, end):
    params = {WINDOW:14, COEFF: 0.5}
    return sequence(key, dic, begin, end, params)
