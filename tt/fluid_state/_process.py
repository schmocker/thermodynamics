from tabulate import tabulate
from . import Fluid

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