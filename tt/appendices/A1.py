import os
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
from scipy.interpolate import interp1d



class SaturatedWater:
    _data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'A1.xlsx')
    _data = pd.read_excel(_data_path, sheet_name='A-1', usecols="A:K")

    _prop_unit = {s.split()[0]: s.split(' ', 1)[1][1:-1] for s in _data.columns}
    _data.columns = _prop_unit.keys()

    units = _prop_unit.values()
    properties = _data.columns.to_list()

    def __init__(self, key: str='T (°C)', value: float=20):
        self.properties = self.get_state(key, value)

        """
        neue Idee: irgend ein Wert (T, P, uv, ...) kann gegeben werden,
        alle anderen Werte werden Interpoliert
        """


    @classmethod
    def get_state(cls, key: str, value: float):
        properties = dict()
        for col_name in cls.properties:
            ipl = interp1d( cls._data[key], cls._data[col_name])
            properties[col_name] = ipl(value).tolist()
        return properties

    @property
    def T(self) -> float:
        return self.properties['T (°C)']

    @property
    def P(self) -> float:
        return self.properties['P (bar)']

    @property
    def vf(self) -> float:
        return self.properties['vf (m3/kg)']



if __name__ == "__main__":
    print(SaturatedWater.get_state('T (°C)', 20))

    sw = SaturatedWater()
    print(sw.vf)

    r=5

# path = 'C:\\Users\\timothy.griffin\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\tt1_Appendices'
# df = pd.read_excel(str(path) + '\Thd Skript Anhang Tabelle A-01 Rev07.xlsx', sheet_name='A-1')
# T = np.array(df['T (°C)'])
# P = np.array(df['P (bar)'])
# vf = np.array(df['vf (m3/kg)'])
# vg = np.array(df['vg (m3/kg)'])
# uf = np.array(df['uf (kJ/kg)'])
# ug = np.array(df['ug (kJ/kg)'])
# hf = np.array(df['hf (kJ/kg)'])
# hfg = np.array(df['hfg (kJ/kg)'])
# hg = np.array(df['hg (kJ/kg)'])
# sf = np.array(df['sf (kJ/(kg K))'])
# sg = np.array(df['sg (kJ/(kg K))'])

# interpolations based on temperature

def vg_water(T_value):
    vg_value = interp1d(T,vg)
    return vg_value(T_value)

def uf_water(T_value):
    uf_value = interp1d(T,uf)
    return uf_value(T_value)

def ug_water(T_value):
    ug_value = interp1d(T,ug)
    return ug_value(T_value)

def hf_water(T_value):
    hf_value = interp1d(T,hf)
    return hf_value(T_value)

def hfg_water(T_value):
    hfg_value = interp1d(T,hfg)
    return hfg_value(T_value)

def hg_water(T_value):
    hg_value = interp1d(T,hg)
    return hg_value(T_value)

def sf_water(T_value):
    sf_value = interp1d(T,sf)
    return sf_value(T_value)

def sg_water(T_value):
    sg_value = interp1d(T,sg)
    return sg_value(T_value)

def Psat_water(T_value): # value in bar
    Psat_value = interp1d(T,P)
    return Psat_value(T_value)

def Tsat_water(P_value): # value in °C
    Tsat_value = interp1d(P,T)
    return Tsat_value(P_value)

