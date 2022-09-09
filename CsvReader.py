# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 14:06:38 2022

@author: docs9
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './'))

import pandas as pd
from datetime import datetime, timezone, timedelta
from utility import df2dic, jst2timestamp

from const import *


def timestamp2pydatetime(array):
    out = []
    for a in array:
        out.append(a.to_pydatetime())
    return out

def datetime64pydatetime(array):
    out = []
    for a in array:
        out.append(a.astype(datetime))
    return out

def string2pydatetime(array:list, form='%Y-%m-%d %H:%M:%S%z', localize=True, offset=None):
    out = []
    for s in array:
        values = s.split('+')
        t = datetime.strptime(values[0], form)
        if offset is not None:
            t += offset
        if localize:
            t = t.astimezone()
        out.append(t)
    return out    





class CsvReader(object):

    def __init__(self):
        pass
            
    @classmethod        
    def loadTradingviewCsv(cls, filepath):
        df = pd.read_csv(filepath)
        df = df.rename(columns={'time': TIMEJST})
        #print(df.head())
        jst = string2pydatetime(df[TIMEJST].values, form='%Y-%m-%dT%H:%M:%S')
        df[TIMESTAMP] = jst2timestamp(jst)
        df1 = df[[TIMESTAMP, OPEN, HIGH, LOW, CLOSE]]
        data = df2dic(df1, is_numpy=False)
        data[TIMEJST] = jst
        return data, len(jst)
    
    @classmethod 
    def loadBitflyerCsv(cls, filepath):
        df = pd.read_csv(filepath)
        df = df.rename(columns={'time': TIMEJST})
        jst = string2pydatetime(df[TIMEJST].values, form='%Y-%m-%d %H:%M:%S', offset=timedelta(hours=9))
        df[TIMESTAMP] = jst2timestamp(jst)
        df1 = df[[TIMESTAMP, OPEN, HIGH, LOW, CLOSE]]
        data = df2dic(df1, is_numpy=False)
        data[TIMEJST] = jst
        return data , len(jst)
            
    @classmethod         
    def loadMt5Csv(cls, filepath):
        df = pd.read_csv(filepath)
        jst = string2pydatetime(df[TIMEJST].values)
        df1 = df[[TIMESTAMP, OPEN, HIGH, LOW, CLOSE, VOLUME]]
        data = df2dic(df1, is_numpy=False)
        data[TIMEJST] = jst
        return data, len(jst)