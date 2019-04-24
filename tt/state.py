import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI
# from .pv_chart import PvChart
import pint
import pandas as pd
import os
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

ureg = pint.UnitRegistry()
_properties_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Properties.xlsx')


class AbstractFluid:
    def __init__(self, fluid_name):
        self.fluid_name = fluid_name

        T_crit = PropsSI('T_critical', fluid_name) * ureg.K
        p_crit = PropsSI('p_critical', fluid_name) * ureg.Pa
        properties_crit = {'T': T_crit, 'p': p_crit}
        self.critical_point = FluidState(fluid_name=fluid_name, properties=properties_crit)

        T_triple = PropsSI('T_triple', fluid_name) * ureg.K
        properties_triple_liquid = {'x': 0, 'T': T_triple}
        self.triple_point_liquid = FluidState(fluid_name=fluid_name, properties=properties_triple_liquid)
        properties_triple_vapor = {'x': 1, 'T': T_triple}
        self.triple_point_vapor = FluidState(fluid_name=fluid_name, properties=properties_triple_vapor)

    def get_saturation_line(self, x: int, space_property: str, space: str = 'linear', n_points: int = 10):
        if x is 0:
            prop_min = self.triple_point_liquid.get_property(space_property)
        elif x is 1:
            prop_min = self.triple_point_vapor.get_property(space_property)
        else:
            raise ValueError('property x of saturation_line must be 0 or 1')
        prop_max = self.critical_point.get_property(space_property)
        return self.get_iso_line('x', x, space_property, prop_min, prop_max, space, n_points)

    def get_triple_line(self, space: str = 'linear', n_points: int = 10):
        prop_min = self.triple_point_liquid.v
        prop_max = self.triple_point_vapor.v
        iso_prop = self.triple_point_vapor.p
        return self.get_iso_line('p', iso_prop, 'v', prop_min, prop_max, space, n_points)

    def get_iso_line(self, iso_property_name, iso_property_value, space_property,
                     space_min=None, space_max=None, space='linear', n_points=10):
        space_unit = space_min.units
        space_max = space_max.to(space_unit)
        if space == 'linear':
            range = [m * space_unit for m in np.linspace(space_min.magnitude, space_max.magnitude, n_points)]
        elif space == 'log':
            range = [m * space_unit for m in np.logspace(np.log10(space_max.magnitude), np.log10(space_min.magnitude), n_points)]
        else:
            raise ValueError(f'"{space}" is not valid for property "space"')
        properties = [{iso_property_name: iso_property_value, space_property: v} for v in range]
        return [FluidState(fluid_name=self.fluid_name, properties=p) for p in properties]

    @property
    def T_triple(self) -> ureg.Quantity:
        return self.get_property('T_triple')

    @property
    def p_triple(self) -> ureg.Quantity:
        return self.get_property('p_triple')


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


class Fluid(AbstractFluid, FluidState):
    def __init__(self, fluid_name: str, properties: dict, amount):
        AbstractFluid.__init__(self, fluid_name=fluid_name)
        FluidState.__init__(self, fluid_name=fluid_name, properties=properties)
        self._amount = amount

    @property
    def m(self):
        if self._amount is None:
            self._amount = 0 * ureg.kg
        elif type(self._amount) is float or type(self._amount) is int:
            self._amount = self._amount * ureg.kg
        elif type(self._amount) is ureg.Quantity:
            base_unit = self._amount.to_base_units().units
            if base_unit == ureg.kg:
                pass
            elif base_unit == ureg.mol:
                self._amount = self.M * self._amount
            elif base_unit == ureg.m ** 3:
                self._amount = self.rho * self._amount
            else:
                raise ValueError(f"for amount of type '{ureg.Quantity}' following base units are valid: "
                                 f"- {ureg.kg}"
                                 f"- {ureg.mol}"
                                 f"- {ureg.m ** 3}")
            self._amount = self._amount.to(ureg.kg)
        else:
            raise ValueError(f"amount can ether be:\n"
                             f"- 'None' for specific Fluid calculations,"
                             f"- of type 'float' or 'int' in kg"
                             f"- of type '{ureg.Quantity}' ")
        return self._amount

    @property
    def n(self) -> ureg.Quantity:
        return self.m / self.M

    @property
    def V(self) -> ureg.Quantity:
        return self.m / self.rho

    @property
    def S(self) -> ureg.Quantity:
        return self.s * self.m

    @property
    def U(self) -> ureg.Quantity:
        return self.u * self.m

    @property
    def H(self) -> ureg.Quantity:
        return self.h * self.m

    @property
    def F(self) -> ureg.Quantity:
        return self.f * self.m

    @property
    def G(self) -> ureg.Quantity:
        return self.g * self.m

    def __add__(self, another_fluid: 'Fluid'):
        if self._fluid != another_fluid._fluid:
            raise ValueError('only equal fluids can be mixed')
        else:
            raise NotImplementedError('fluid mixing not jet implemented')
            m1 = self.m
            m2 = self.m
            if m1.magnitude is 0 or m2.magnitude is 0:
                raise ValueError('one of the fluids has no mass')
            m_tot = m1 + m2

            T = (self.T * m1 + another_fluid.T * m2) / m_tot

            p = 0
            props = {'T': T, 'p': p}
            new_fluid = Fluid(self._fluid, m_tot, **props)

            return new_fluid


class Process:
    def __init__(self, fluid: Fluid, iso_property_name: str, changing_property_name: str, changing_property_value):
        self.iso_property_name = iso_property_name
        self.changing_property_name = changing_property_name
        self.state_1 = fluid
        self.state_2 = self.process_iso_to(fluid, iso_property_name, changing_property_name, changing_property_value)

    def __repr__(self):
        return f'Process({self.state_1} -> {self.state_2})'

    def get_difference_of(self, property_name):
        return self.state_2.get_property(property_name) - self.state_1.get_property(property_name)

    @staticmethod
    def process_iso_to(fluid: Fluid, iso_property_name: str,
                       changing_property_name: str, changing_property_value: float):
        iso_property_value = fluid.get_property(iso_property_name)
        properties = {changing_property_name: changing_property_value,
                      iso_property_name: iso_property_value}
        return Fluid(fluid_name=fluid.fluid_name, amount=fluid.m, properties=properties)

    def summary(self):
        print(f'\nSummary for {self}')
        t_header = ['Property', 'From', 'To', 'Difference', 'Unit', 'Iso']
        t_data = []
        for p, r in Fluid.properties.iterrows():
            iso_prop = '*' if p == self.iso_property_name else ''
            t_data.append([p, self.state_1.get_property(p).magnitude, self.state_2.get_property(p).magnitude,
                           self.get_difference_of(p).magnitude, self.state_1.get_property(p).units, iso_prop])
        print(tabulate(t_data, t_header, tablefmt="orgtbl", floatfmt=".2f"))


class ThermoChart:
    KINDS = ['pv', 'ts']

    def __init__(self, kind: str, fluid: str, x_property: str, x_unit:str, y_property:str, y_unit:str,
                 states=None, processes=None, show=True, x_log:bool=False, y_log:bool=False):
        if kind not in self.KINDS:
            raise ValueError(f'kind "{kind}" not in {self.KINDS}')
        self.kind = kind

        self.fluid = AbstractFluid(fluid)

        states = [] if states is None else states
        states = [states] if type(states) is not list else states
        self.states = states

        processes = [] if processes is None else processes
        processes = [processes] if type(processes) is not list else processes
        self.processes = processes

        self.property_x = x_property
        self.unit_x = ureg.Unit(x_unit)
        self.property_y = y_property
        self.unit_y = ureg.Unit(y_unit)

        self.fig = None

        self.x_log = x_log
        self.y_log = y_log

    def add_point(self, ax, fluid: FluidState, **kwargs):
        fluid = [fluid] if type(fluid) is not list else fluid
        x = [f.get_property(self.property_x).to(self.unit_x).magnitude for f in fluid]
        y = [f.get_property(self.property_y).to(self.unit_y).magnitude for f in fluid]
        ax.scatter(x, y, **kwargs)

    def add_line(self, ax, line: list, **kwargs):
        x = [f.get_property(self.property_x).to(self.unit_x).magnitude for f in line]
        y = [f.get_property(self.property_y).to(self.unit_y).magnitude for f in line]
        ax.plot(x, y, **kwargs)

    def create_empty(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        self.add_point(ax, self.fluid.critical_point, label='critical point', c='r')
        self.add_point(ax, self.fluid.triple_point_liquid, label='triple point (liquid)', c='r')
        self.add_point(ax, self.fluid.triple_point_vapor, label='triple point (vapor)', c='r')

        sat_line = self.fluid.get_saturation_line(x=0, space_property='p', n_points=100, space='linear')
        self.add_line(ax, sat_line, label='saturated liquid line')

        sat_line = self.fluid.get_saturation_line(x=1, space_property='p', n_points=100, space='linear')
        self.add_line(ax, sat_line, label='saturated vapor line')

        triple_line = self.fluid.get_triple_line(n_points=100)
        self.add_line(ax, triple_line, label='triple line')

        for s in self.states:
            x = s.get_property(self.property_x).to(self.unit_x)
            y = s.get_property(self.property_y).to(self.unit_y)
            label = f'{s.fluid_name}({self.property_x}: {"{:.3g~P}".format(x)}, {"{:.3g~P}".format(y)})'
            self.add_point(ax, s, label=label)

        for p in self.processes:
            iso_property = p.state_1.get_property(p.iso_property_name)
            line = p.state_1.get_iso_line(p.iso_property_name, iso_property,
                                          p.changing_property_name,
                                          p.state_1.get_property(p.changing_property_name),
                                          p.state_2.get_property(p.changing_property_name), n_points=100, space='log')
            label = f'Iso: {p.iso_property_name}@{"{:.3g~P}".format(iso_property)}'
            self.add_line(ax, line, label=label)

        plt.xlabel(f'{self.property_x} [{"{:~P}".format(self.unit_x)}]')
        plt.ylabel(f'{self.property_y} [{"{:~P}".format(self.unit_y)}]')

        if self.x_log:
            ax.set_xscale('log')
        else:
            # ax.set_xlim([0,0.05])
            pass

        if self.y_log:
            ax.set_yscale('log')

        plt.legend(loc='best')

        plt.show()


if __name__ == "__main__":
    props = {'p': 100, 'v': 0.02}
    f1 = Fluid(fluid_name='Water', amount=1, properties=props)
    p12 = Process(f1, 'p', 'T', 400)

    f2 = p12.state_2
    p23 = Process(f2, 'T', 'p', 230)
    f3 = p23.state_2
    p34 = Process(f3, 'p', 'v', 0.002)
    f4 = p34.state_2
    p45 = Process(f4, 'T', 'v', 1)
    f5 = p45.state_2

    chrt = ThermoChart('pv', fluid=f1.fluid_name, x_property='h', x_unit='kJ/kg', y_property='p', y_unit='bar',
                       states=[f1, f2, f3, f4, f5], processes=[p12, p23, p34, p45], x_log=False, y_log=False)

    chrt.create_empty()

    f1.summary()

    p12 = Process(f1, 'p', 'T', 400)
    p12.summary()
    f2 = p12.state_2
