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
    base_names = ['std-1br-dwh','std-2br-dwh','std-3br-dwh','std-4br-dwh','std-5br-dwh']
    month = 1
    
    print ('Total energy: ', heatingEnergy(120, 50, 60)) # base formula
    print ('Total energy: ', 2.44*60*70) # Anne's equation for energy as a check
    
    for name in base_names:
        group = loadData(f'outputs/grouped-{name}-{month}.csv')
        group = group.assign(energy = lambda x: (heatingEnergy(120, 50, x['draws'])))
        print(f'{name} energy: {group.energy.sum()}')
        group.to_csv(f'outputs/energy-{name}-{month}.csv')
        plt.figure()
        plt.plot(group.energy, color=plt.cm.PuBuGn(1/1))
        plt.xlabel('Time (seconds)')
        plt.ylabel('Energy (wh)')
        plt.savefig(f'outputs/energy-{name}-{month}.png', bbox_inches='tight')
        
    for name in base_names:
        group = loadData(f'outputs/grouped-{name}-{month}.csv')
        plt.figure()
        plt.plot(group.draws, color=plt.cm.PuBuGn(1/1))
        plt.xlabel('Time (seconds)')
        plt.ylabel('Water (gallons)')
        plt.savefig(f'outputs/{name}-{month}.svg', bbox_inches='tight')
        plt.savefig(f'outputs/{name}-{month}.png', bbox_inches='tight')