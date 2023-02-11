import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

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
    TIME_FORMAT = '%m/%d %I:%M:%S %p'
    data['Time'] = pd.to_datetime(data['Time'],format=TIME_FORMAT)
    data['Duration'] = pd.to_timedelta(data['Duration'], unit='s')
    return data
        
def toEvents(data:pd.DataFrame) -> np.ndarray:
    n = len(data)
    events = np.empty(n, dtype=Event)
    for idx, row in data.iterrows():
        start = row['Time']
        end = start + row['Duration']
        draw = row['Duration'].seconds*row['Hot']/60
        events[idx] = Event(start, end, draw)
    return events

def stackEvents(events:np.ndarray) -> np.ndarray:
    SECONDS_PER_DAY = 60*60*24
    draws = np.empty(SECONDS_PER_DAY)
    
if __name__ == '__main__':
    raw = loadData('data/std-3br-dwh.csv')
    data = toTimeSeries(raw)
    events = toEvents(data)
    print(events)