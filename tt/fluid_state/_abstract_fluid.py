from CoolProp.CoolProp import PropsSI
import numpy as np
from . import ureg, FluidState


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