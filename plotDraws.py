import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

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