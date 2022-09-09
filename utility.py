# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 20:24:47 2022

@author: docs9
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone

def df2dic(df: pd.DataFrame, is_numpy=True, time_key = 'time', convert_keys=None):
    columns = df.columns
    dic = {}
    for column in columns:
        d = None
        if column.lower() == time_key.lower():
            d = df[column].values
        else:
            d = df[column].values.tolist()
            d = [float(v) for v in d]
            if is_numpy:
                d = np.array(d)
        if convert_keys is None:
            key = column
        else:
            try:
                key = convert_keys[column]
            except Exception as e:
                key = column
        dic[key] = d
    return dic

def dic2df(dic):
    keys = list(dic.keys())
    values = list(dic.values())

    n = len(values)
    length = len(values[0])
    
    out = []
    for i in range(length):
        d = []
        for j in range(n):
            d.append(values[j][i])
        out.append(d)
    df = pd.DataFrame(data=out, columns = keys)
    return df

    
def splitDic(dic, i):
    keys = dic.keys()
    arrays = []
    for key in keys:
        arrays.append(dic[key])
    split1 = {}
    split2 = {}
    for key, array in zip(keys, arrays):
        split1[key] = array[:i]
        split2[key] = array[i:]
    return (split1, split2)
    
    
def deleteLast(dic):
    keys = dic.keys()
    arrays = []
    for key in keys:
        arrays.append(dic[key])
    out = {}
    for key, array in zip(keys, arrays):
        out[key] = array[:-1]
    return out        
        

def sliceDic(dic, begin, end):
    keys = dic.keys()
    arrays = []
    for key in keys:
        arrays.append(dic[key])
    out = {}
    for key, array in zip(keys, arrays):
        out[key] = array[begin: end + 1]
    return out
        
def dic2Arrays(dic):
    keys = dic.keys()
    arrays = []
    for key in keys:
        arrays.append(dic[key])
    return keys, arrays

def sliceTime(pytime_array: list, time_from, time_to):
    begin = None
    end = None
    for i in range(len(pytime_array)):
        t = pytime_array[i]
        if begin is None:
            if t >= time_from:
                begin = i
        else:
            if t > time_to:
                end = i
                return (end - begin + 1, begin, end)
    if begin is not None:
        end = len(pytime_array) - 1
        return (end - begin + 1, begin, end)
    else:
        return (0, None, None)
    
def insertDicArray(dic: dict, add_dic: dict):
    keys = dic.keys()
    try:
        for key in keys:
            a = dic[key]
            a += add_dic[key]
        return True
    except:
        return False
    
def jst2timestamp(jst):
    timestamp = []
    for t in jst:
        timestamp.append(t.timestamp())
    return timestamp
    
def jst2utc(jst):
    utc = []
    for t in jst:
        utc.append(t.astimezone(timezone.utc))
    return utc
    
    

    