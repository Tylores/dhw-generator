import numpy as np
import pandas as pd
import datetime

KG_PER_GALLON = 3.7854
SPECIFIC_HEAT_H2O = 4190
JOULE_PER_WATT_HOUR = 3600

def load_data(filepath: str) -> pd.DataFrame:
    data = pd.read_csv(filepath)
    if data.isnull().values.any():
        print('data is missing values')
        exit()
    return data

def to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32)/1.8

def to_kilograms(gallons: float) -> float:
    return KG_PER_GALLON*gallons

def heating_energy(temp_2: float, temp_1: float, volume: float) -> float:
    c = SPECIFIC_HEAT_H2O
    m = to_kilograms(volume)
    t2 = to_celsius(temp_2)
    t1 = to_celsius(temp_1)
    return c*m*(t2-t1)/JOULE_PER_WATT_HOUR

def temp_change(temp: float, volume: float, energy: float) -> float:
    c = SPECIFIC_HEAT_H2O
    m = to_kilograms(volume)
    t1 = to_celsius(temp)
    return (energy*JOULE_PER_WATT_HOUR)/(c*m) + t1

def tank_temp(t1: float, m1: float, t2: float, m2: float) -> float:
    """internal energy balance
    """
    return (m1*t1 + m2*t2)/(m1+m2)

def ambient_loss(temp: float) -> float:
    """TODO
    """
    return temp - temp/100

class WaterHeater():
    """Electric Water Heater Simulator
    """    
    def __init__(self, volume, temp_setpoint, event_profile: pd.DataFrame) -> None:
        self.VOLUME = volume
        self.TEMP_SETPOINT = temp_setpoint
        self.TEMP_INLET = 50
        self.POWER = 4500
        self.load_profile(event_profile)
        self.data.to_csv(f'outputs/water-sim.csv')
        
    def load_profile(self, events: pd.DataFrame) -> None:
        timestamps = pd.date_range(events['start_time'][0], events['start_time'][len(events)-1], freq='S')
        draws = np.zeros(len(timestamps), dtype=float)
        temp = np.ones(len(timestamps), dtype=float)*self.TEMP_SETPOINT
        energy = np.zeros(len(timestamps), dtype=float)
        power = np.zeros(len(timestamps), dtype=float)
        self.data = pd.DataFrame({'draws': draws, 'temp':temp, 'energy':energy, 'power':power}, index=timestamps)
        
        idx = 0
        last_temp = self.TEMP_SETPOINT
        for  idx, row in self.data.iterrows():
            start = events['start_time'][idx]
            end = events['end_time'][idx]
            if idx <= end and idx >= start:
                row.draws = events['draw'][idx]
                row.temp = tank_temp(last_temp, self.VOLUME-row.draws, self.TEMP_INLET, row.draws)
                row.energy = heating_energy(self.TEMP_SETPOINT, row.temp, self.VOLUME)
            else:
                idx+=1
            if (last_temp <= self.TEMP_SETPOINT):
                row.power = self.POWER
                row.temp = temp_change(row.temp, self.VOLUME, row.power/3600)
                row.energy = heating_energy(self.TEMP_SETPOINT, row.temp, self.VOLUME)
                
            last_temp = ambient_loss(row.temp)
            
if __name__ == '__main__':
    name = 'std-1br-dwh'
    profile = load_data(f'outputs/unique/{name}-1.csv')  
    print(profile)       
    WaterHeater(80, 120, profile)
                
        
    