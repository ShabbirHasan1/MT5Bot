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
    
class MarketData:
    
    def __init__(self, name, interval, unit, is_volume):
        self.name = name
        self.interval = interval
        self.unit = unit
        self.is_volume = is_volume
        self.df = pd.DataFrame(columns = COLUMNS)
        pass
    
    def setDataFrame(self, df):
        self.df = df
            
    def beginTime(self):
        t = self.df.iloc[0].time
        return t
    
    def endTime(self):
        t = self.df.iloc[-1].time
        return t
    
    def timeRangeFilter(self, begin, end):
        d0 = self.df[self.df['time'] >= begin]
        d1 = d0[d0['time'] <= end]
        return d1
    
    def tohlcvList(self):
        times = self.pytime()
        #times = self.df['time'].strftime('%Y-%m-%d %H:%M:%S')
        oo = self.df['open'].values.tolist()
        hh = self.df['high'].values.tolist()
        ll = self.df['low'].values.tolist()
        cc = self.df['close'].values.tolist()
        vv = np.zeros(len(oo))
        data = []
        for t, o, h, l, c, v in zip(times, oo, hh, ll, cc, vv):
            data.append([t, o, h, l, c, v])
        return data
    
    def tohlcList(self):
        times = self.pytime()
        #times = self.df['time'].strftime('%Y-%m-%d %H:%M:%S')
        oo = self.df['open'].values.tolist()
        hh = self.df['high'].values.tolist()
        ll = self.df['low'].values.tolist()
        cc = self.df['close'].values.tolist()
        data = []
        for t, o, h, l, c in zip(times, oo, hh, ll, cc):
            data.append([t, o, h, l, c])
        return data
    
    def ohlcArray(self):
        o = self.df['open'].values.tolist()
        h = self.df['high'].values.tolist()
        l = self.df['low'].values.tolist()
        c = self.df['close'].values.tolist()
        data = [o, h, l, c]
        return np.array(data).T
    
    def ohlcvArray(self):
        o = self.df['open'].values.tolist()
        h = self.df['high'].values.tolist()
        l = self.df['low'].values.tolist()
        c = self.df['close'].values.tolist()
        if self.is_volume:
            v = self.df['volume'].values.tolist()
        else:
            v = np.zeros(len(o))
        data = [o, h, l, c, v]
        return np.array(data).T
    
    def ohlc(self):
        o = self.df['open'].values.tolist()
        h = self.df['high'].values.tolist()
        l = self.df['low'].values.tolist()
        c = self.df['close'].values.tolist()
        return [o, h, l, c]
    
    def length(self):
        return len(self.df)
    
    def pdtime(self):
        return self.df.time
    
    def pytime(self):
        times = []
        for time in self.df.time:
            t = time.to_pydatetime()
            times.append(t)
        return times
    
    def timeStr(self, form = '%Y-%m-%d %H:%M:%S'):
        return self.df['time'].strftime(form)
    
    def tohlc(self):
        return [self.df.time, self.df.open, self.df.high, self.df.low, self.df.close]
    
    def importFromSQLite(self, db_filepath, table_name):
        db = SQLite.SQLite(db_filepath)
        df = db.fetch(table_name)
        self.setDataFrame(df)
        return df
        
    def importFromCsv(self, filepath):
        df0 = pd.read_csv(filepath, encoding = 'shiftjis')
        df = self.convert(df0, self.str2datetime1)
        self.df = df
        pass        
    
    def importClickSecFiles(self, file_list):
        for file in file_list:
            df = self.importClicSecFile(file)
            print(len(df), '... done')
            self.df = self.df.append(df, ignore_index=True)
        print('<<< end')
        pass
    
    def exportToSQLight(self, filepath, table_name):
        db = SQLite.SQLite(filepath)
        db.create(table_name)
        db.insert(table_name, self.df.values)
        pass
    
    def convert(self, df, func):
        tlist = df.iloc[:, 0].values.tolist()
        time = []
        for t in tlist:
            tt = func(str(t))
            time.append(tt)
        values = {}
        for i in range(len(COLUMNS)):
            column = COLUMNS[i]
            if i == 0:
                values[column] = time
            else:
                if self.is_volume == False and i == len(COLUMNS) -1:
                    values[column] = np.zeros(len(time)).tolist()
                else:
                    values[column] = df.iloc[:, i].values.tolist()
        out = pd.DataFrame(data = values, columns =COLUMNS, index = time)
        return out
            
    def str2datetime1(self, text):
        t = datetime.datetime.strptime(text, '%Y/%m/%d %H:%M:%S')
        return t
    
    def str2datetime2(self, text):
        s = text[0:4] + '-' + text[4:6] + '-' + text[6:8] + ' ' + text[8:10] + ':' + text[10:12]
        return pd.to_datetime(s)
        
    # for cfd
    def importClicSecFile(self, filepath):
        df0 = pd.read_csv(filepath, encoding='shiftjis')
        table = df0.values.tolist()
        df = self.tableToDf(table)
        return df

    def tableToDf(self, table):
        out = pd.DataFrame(columns = COLUMNS)
        for data in table:
            dic = {}
            if type(data[0]) is int or type(data[0]) is float:
                t = self.str2datetime2(str(int(data[0])))
            else:
                t = self.str2datetime1(str(data[0]))
            dic[COLUMNS[0]] = t
            dic[COLUMNS[1]] = float(data[1])
            dic[COLUMNS[2]] = float(data[2])
            dic[COLUMNS[3]] = float(data[3])
            dic[COLUMNS[4]] = float(data[4])
            if self.is_volume:
                dic[COLUMNS[5]] = float(data[5])
            else:
                dic[COLUMNS[5]] = 0.0
            out = out.append(pd.Series(dic), ignore_index = True)
        return out

    def roundTime(self, time, interval, unit):
        if unit == UNIT_MINUTE:
            t = datetime.datetime(time.year, time.month, time.day, time.hour, 0, 0)
        elif unit == UNIT_HOUR:
            t = datetime.datetime(time.year, time.month, time.day, 0, 0, 0)
        elif unit == UNIT_DAY:
            t = datetime.datetime(time.year, time.month, time.day, 0, 0, 0)
            return t
        if t == time:
            return t
        
        while t < time:
            if unit == UNIT_MINUTE:
                t += datetime.timedelta(minutes = interval)
            elif unit == UNIT_HOUR:
                t += datetime.timedelta(hours = interval)
        return t
    
    def candlePrice(self, time, data):
        o = data[0][0]
        c = data[-1][3]
        h = None
        l = None
        v = 0
        for d in data:
            v += d[4]
            if h is None:
                h = d[1]
                l = d[2]
            else:
                if d[1] > h:
                    h = d[1]
                if d[2] < l:
                    l = d[2]
        return [time, o, h, l, c, v]
    
    def resample(self, interval, unit):
        current_time = None
        table = self.df[['time', 'open', 'high', 'low', 'close', 'volume']].values.tolist()
        out = []
        data = []
        times = []
        for d in table:
            t = pd.to_datetime(d[0])
            round_t = self.roundTime(t, interval, unit)
            values = d[1:6]
            if current_time is None:
                current_time = round_t
                data = [values]
            else:
                if round_t == current_time:
                    data.append(values)
                else:
                    dd = self.candlePrice(current_time, data)
                    times.append(current_time)
                    out.append(dd)
                    current_time = round_t
                    data = [values]  
        df = pd.DataFrame(out, columns = COLUMNS, index = times)
        p = Market(self.name, interval, unit, self.is_volume)
        p.setDataFrame(df)
        return p