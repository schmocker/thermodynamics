import os
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
from scipy.interpolate import interp1d


class IdealGas:
    _data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'A3.xlsx')
    _data = pd.read_excel(_data_path, sheet_name='A-7.1', usecols="A:D")

    _prop_unit = {s.split()[0]: s.split(' ', 1)[1][1:-1] for s in _data.columns}
    _data.columns = _prop_unit.keys()

    units = _prop_unit.values()
    properties = _data.columns.to_list()

    def __init__(self, key: str = 'T (K)', value: float = 273.15):
        self.properties = self.get_state(key, value)

    @classmethod
    def get_state(cls, key: str, value: float):
        properties = dict()
        for col_name in cls.properties:
            ipl = interp1d(cls._data[key], cls._data[col_name])
            properties[col_name] = ipl(value).tolist()
        return properties
