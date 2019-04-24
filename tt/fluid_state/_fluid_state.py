import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI
import pandas as pd
from tabulate import tabulate
import numpy as np
from . import ureg, _properties_path


class FluidState:
    properties = pd.read_excel(_properties_path, sheet_name='Properties')
    properties.set_index('sign', inplace=True)
    for i, r in properties.iterrows():
        properties.loc[i, 'unit'] = ureg.Unit(properties.loc[i, 'unit'])
        try:
            properties.loc[i, 'coolprop_unit'] = ureg.Unit(properties.loc[i, 'coolprop_unit'])
        except Exception:
            pass

    def __init__(self, fluid_name: str, properties: dict):
        self.fluid_name = fluid_name
        self.cp_inputs = {}
        for pn, value in properties.items():
            if pn == 'v':
                value = 1 / value
                pn = 'rho'

            if pn not in self.properties.loc[self.properties.valid_input == True].index:
                raise ValueError(f'{pn} is not a possible property name')

            p = self.properties.loc[pn]
            if type(value) is ureg.Quantity:
                value = value.to(p['coolprop_unit'])
            else:
                try:
                    value = (value * p.unit).to(p['coolprop_unit'])
                except Exception as e:
                    raise ValueError(f'{value} is not a possible value for property name {pn}')

            self.cp_inputs[p['coolprop_sign']] = value

        if len(self.cp_inputs) != 2:
            raise ValueError(f'properties must have exactly 2 key value pairs but {len(self.cp_inputs)} were given')

    @property
    def T(self) -> ureg.Quantity:
        return self.get_property('T')

    @property
    def p(self) -> ureg.Quantity:
        return self.get_property('p')

    @property
    def x(self) -> ureg.Quantity:
        return self.get_property('x')

    @property
    def M(self) -> ureg.Quantity:
        return self.get_property('M')

    @property
    def rho(self) -> ureg.Quantity:
        return self.get_property('rho')

    @property
    def v(self) -> ureg.Quantity:
        return 1 / self.rho

    @property
    def phase(self) -> ureg.Quantity:
        return self.get_property_from_coolprop('phase')

    @property
    def s(self) -> ureg.Quantity:
        return self.get_property('s')

    @property
    def s_molar(self) -> ureg.Quantity:
        return self.get_property('s_molar')

    @property
    def u(self) -> ureg.Quantity:
        return self.get_property('u')

    @property
    def u_molar(self) -> ureg.Quantity:
        return self.get_property('u_molar')

    @property
    def h(self) -> ureg.Quantity:
        return self.get_property('h')

    @property
    def h_molar(self) -> ureg.Quantity:
        return self.get_property('h_molar')

    @property
    def cv(self) -> ureg.Quantity:
        return self.get_property('cv')

    @property
    def cv_molar(self) -> ureg.Quantity:
        return self.get_property('cv_molar')

    @property
    def cp(self) -> ureg.Quantity:
        return self.get_property('cp')

    @property
    def cp_molar(self) -> ureg.Quantity:
        return self.cp * self.M

    @property
    def f(self) -> ureg.Quantity:
        return self.get_property('f')

    @property
    def f_molar(self) -> ureg.Quantity:
        return self.get_property('f_molar')

    @property
    def g(self) -> ureg.Quantity:
        return self.get_property('g')

    @property
    def g_molar(self) -> ureg.Quantity:
        return self.get_property('g_molar')

    @property
    def rho_molar_c(self) -> ureg.Quantity:
        return self.get_property('rho_molar_c')

    def __repr__(self):
        keys = list(self.cp_inputs.keys())
        values = list(self.cp_inputs.values())
        return f'{self.fluid_name}({keys[0]}: {values[0]} / {keys[1]}: {values[1]})'

    def get_property(self, property_name: str):
        if property_name == 'm':
            return self.m
        else:
            p = self.properties.loc[property_name]
            cp_pn = p['coolprop_sign']
            cp_unit = p['coolprop_unit']
            try:
                if not p.coolprop_use:
                    return getattr(self, property_name)
                else:
                    if cp_pn in self.cp_inputs.keys():
                        v = self.cp_inputs[cp_pn]
                    else:
                        v = self.get_property_from_coolprop(cp_pn)
                        v = v * cp_unit
                    return v.to(p['unit'])
            except Exception as e:
                if cp_pn not in self.properties.coolprop_sign.tolist():
                    raise ValueError(f"'{property_name}' is no valid property name")
                else:
                    raise e

    def get_property_from_coolprop(self, coolprop_property_name: str):
        if coolprop_property_name in ['T_critical', 'p_critical', 'rhomass_critical', 'rhomolar_critical',
                                      'T_triple', 'p_triple']:  # todo: add reducing point?
            return PropsSI(coolprop_property_name, self.fluid_name)
        pns = list(self.cp_inputs.keys())
        values = list(self.cp_inputs.values())
        try:
            if coolprop_property_name == 'phase':
                return CP.PhaseSI(pns[0], values[0].magnitude, pns[1], values[1].magnitude, self.fluid_name)
            else:
                return PropsSI(coolprop_property_name, pns[0], values[0].magnitude, pns[1], values[1].magnitude,
                               self.fluid_name)
        except Exception as e:
            return np.nan

    def summary(self):
        print(f'\nSummary for {self}')
        t_header = ['Property', 'Value', 'Unit']
        t_data = []
        for p, r in self.properties.iterrows():
            t_data.append([p, self.get_property(p).magnitude, self.get_property(p).units])
        print(tabulate(t_data, t_header, tablefmt="orgtbl", floatfmt=".2f"))