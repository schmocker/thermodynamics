import matplotlib.pyplot as plt
from . import ureg, AbstractFluid, FluidState


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

        return fig