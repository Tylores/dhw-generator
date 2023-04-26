import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.collections import PolyCollection
import math

TIME_FORMAT = '%m/%d %I:%M:%S %p'

class Event():
    def __init__(self, start, end, draw):
        self.start_time = start
        self.end_time = end
        self.water_draw = draw
        
    def __repr__(self) -> str:
        return f"start:{self.start_time}, end: {self.end_time}, draw: {self.water_draw}"

def loadData(filepath: str) -> pd.DataFrame:
    data = pd.read_csv(filepath)
    if data.isnull().values.any():
        print('data is missing values')
        exit()
    return data

def toTimeSeries(data:pd.DataFrame) -> pd.DataFrame:
    data['Time'] = pd.to_datetime(data['Time'],format=TIME_FORMAT)
    data['Duration'] = pd.to_timedelta(data['Duration'], unit='s')
    return data

def perMinute(data:pd.DataFrame) -> pd.DataFrame:
    return data.set_index('timestamps').resample('1min').sum()

def toEvents(data:pd.DataFrame) -> np.ndarray:
    n = len(data)
    events = np.empty(n, dtype=Event)
    ii = 0
    for idx, row in data.iterrows():
        start = row['Time']
        end = start + row['Duration']
        draw = row['Hot']/60
        events[ii] = Event(start, end, draw)
        ii+=1
    return events

def stackEvents(events:np.ndarray) -> pd.DataFrame:
    timestamps = pd.date_range(events[0].start_time, events[-1].end_time, freq='S')
    draws = np.zeros(len(timestamps), dtype=float)
    data = pd.DataFrame({'timestamps': timestamps, 'draws': draws})
    
    for event in events:
        mask = (data['timestamps'] > event.start_time) & (data['timestamps'] < event.end_time)
        data.loc[mask, 'draws'] += event.water_draw
    
    data.draws.round(6)
    return data

def filterZeros(data:pd.DataFrame) -> pd.DataFrame:
    return data[data['draws'] != 0].reset_index()

def compressDraws(data: pd.DataFrame) -> pd.DataFrame:
    data = filterZeros(data)
    N = len(data)

    start_time = np.empty(N, dtype=pd.Timestamp)
    end_time = np.empty(N, dtype=pd.Timestamp)
    draw = np.zeros(N, dtype=float)
    
    ii = 0
    start_time[ii] = data['timestamps'][0]
    draw[ii] = data['draws'][0]
    last_time = start_time[0]
    for idx, row in data.iterrows():
        if not (row.draws == draw[ii]):
            end_time[ii] = last_time
            ii+=1
            start_time[ii] = row.timestamps
            draw[ii] = row.draws
        last_time = row.timestamps
    end_time[ii] = last_time
    
    return pd.DataFrame({'start_time': start_time, 'end_time': end_time, 'draw': draw}).dropna()

if __name__ == '__main__':
    # base_names = ['std-1br-dwh','std-2br-dwh','std-3br-dwh','std-4br-dwh','std-5br-dwh']
    base_names = ['std-3br-dwh']
    
    for name in base_names:
        raw = loadData(f'data/{name}.csv')
        data = toTimeSeries(raw)

        cnt = 1
        for idx, day in data.groupby(data.Time.dt.date):
                print(name, idx)
                events = toEvents(day)
                stacked = stackEvents(events)
                per_minute = perMinute(stacked)
                per_minute.to_csv(f'outputs/{name}-{cnt}-min.csv',index=False)
                print(stacked['draws'].sum(), per_minute.sum())
                compressed = compressDraws(stacked)               
                compressed.to_csv(f'outputs/{name}-{cnt}.csv',index=False)
                cnt+=1
    
