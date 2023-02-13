import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def loadData(filepath: str) -> pd.DataFrame:
    data = pd.read_csv(filepath)
    if data.isnull().values.any():
        print('data is missing values')
        exit()
    return data

if __name__ == '__main__':
    base_names = ['std-1br-dwh','std-2br-dwh','std-3br-dwh','std-4br-dwh','std-5br-dwh']
    month = 1
    
    for name in base_names:
        group = loadData(f'outputs/grouped-{name}-{month}.csv')
        plt.figure()
        plt.plot(group.draws, color=plt.cm.PuBuGn(1/1))
        plt.xlabel('Time (seconds)')
        plt.ylabel('Water (gallons)')
        plt.savefig(f'outputs/{name}-{month}.svg', bbox_inches='tight')
        plt.savefig(f'outputs/{name}-{month}.png', bbox_inches='tight')