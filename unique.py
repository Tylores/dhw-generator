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

    KG_PER_GALLON = 3.7854
    SPECIFIC_HEAT_H2O = 4190
    JOULE_PER_WATT_HOUR = 3600

    def loadData(filepath: str) -> pd.DataFrame:
        data = pd.read_csv(filepath)
        if data.isnull().values.any():
            print('data is missing values')
            exit()
        return data

    def toCelsius(fahrenheit: float) -> float:
        return (fahrenheit - 32)/1.8

    def toKilograms(gallons: float) -> float:
        return KG_PER_GALLON*gallons

    def heatingEnergy(temp_2: float, temp_1: float, volumn: float) -> float:
        c = SPECIFIC_HEAT_H2O
        m = toKilograms(volumn)
        t2 = toCelsius(temp_2)
        t1 = toCelsius(temp_1)
        return c*m*(t2-t1)/JOULE_PER_WATT_HOUR

def polygon_under_graph(x, y):
    """
    Construct the vertex list which defines the polygon filling the space under
    the (x, y) line graph. This assumes x is in ascending order.
    """
    return [(x[0], 0.), *zip(x, y), (x[-1], 0.)]

# Fixing random state for reproducibility
np.random.seed(19680801)
            
if __name__ == '__main__':
    #base_names = ['std-1br-dwh','std-2br-dwh','std-3br-dwh','std-4br-dwh','std-5br-dwh']
    base_names = ['std-1br-dwh']
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    for name in base_names:
        raw = loadData(f'data/{name}.csv')
        data = toTimeSeries(raw)
        
        cnt = 1
        for idx, day in data.groupby(data.Time.dt.date):
                print(idx)
                events = toEvents(day)
                stacked = stackEvents(events)
                compressed = compressDraws(stacked)
                h = stacked.timestamps.dt.hour*60*60
                m = stacked.timestamps.dt.minute*60
                s = stacked.timestamps.dt.second
                x = h+m+s
                x = x.values
                y = stacked.draws.values
                ax.plot(x,y,cnt, zdir='y')
                
                #compressed.to_csv(f'outputs/unique/{name}-{cnt}.csv')
                cnt+=1
                
                if cnt == 20:
                    plt.savefig(f'outputs/{name}-uniques.png', bbox_inches='tight')
    
