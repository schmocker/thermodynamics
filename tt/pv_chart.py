from CoolProp.CoolProp import PropsSI
import numpy as np
import matplotlib.pyplot as plt


class PvChart:
    def __init__(self, fluid: str = 'Water'):
        self.fluid = fluid

        self.T_cirtical = PropsSI("Tcrit", self.fluid)
        self.p_cirtical = PropsSI("Pcrit", self.fluid)
        self.V_cirtical = 1 / PropsSI("rhocrit", self.fluid)

        self.T_trippel = PropsSI("T_triple", self.fluid)
        self.p_trippel = PropsSI("p_triple", self.fluid)

        self.P_range = np.linspace(self.p_trippel, self.p_cirtical, 1000)
        self.V_liquid = 1 / PropsSI("D", "P", self.P_range, "Q", 0, self.fluid)
        self.V_vapor = 1 / PropsSI("D", "P", self.P_range, "Q", 1, self.fluid)

        self.points = []
        self.iso_lines = []

    def _add_isobar_line(self, ax, p):
        v_iso_line = np.logspace(np.log10(0.0008), np.log10(100), 1000)
        p_iso_line = v_iso_line * 0 + p
        ax.plot(v_iso_line, p_iso_line / 1e5,
                label=f'Isobar (p = {p / 1e5} bar)')

    def _add_isotherm_line(self, ax, T):
        v_iso_line = np.logspace(np.log10(0.0008), np.log10(100), 1000)
        p_iso_line = PropsSI("P", "D", 1 / v_iso_line, "T", T, self.fluid)
        ax.plot(v_iso_line[p_iso_line<self.p_cirtical], p_iso_line[p_iso_line<self.p_cirtical] / 1e5,
                label=f'Isotherm (T = {T} K)')

    def _add_isoquality_line(self, ax, x):
        p_iso_line = np.logspace(np.log10(self.p_trippel), np.log10(self.p_cirtical), 100)
        p_iso_line = np.linspace(self.p_trippel, self.p_cirtical, 100)
        v_iso_line = 1 / PropsSI("D", "P", p_iso_line, "Q", x, self.fluid)
        # v_iso_line = np.logspace(np.log10(0.0008), np.log10(100), 100)
        # p_iso_line = PropsSI("P", "D", 1 / v_iso_line, "Q", x, self.fluid)
        ax.plot(v_iso_line, p_iso_line / 1e5, label=f'Isoquality (x = {x})')

    @property
    def figure(self, show=False) -> plt.Figure:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter([self.V_cirtical], [self.p_cirtical / 1e5], label='critical point', c='r')
        ax.plot(self.V_liquid[self.V_liquid > 0], self.P_range[self.V_liquid > 0] / 1e5, label='saturated liquid line')
        ax.plot(self.V_vapor[self.V_vapor > 0], self.P_range[self.V_vapor > 0] / 1e5, label='saturated vapor line')

        # draw iso lines
        for iso_line in self.iso_lines:
            prop = iso_line['property']
            value = iso_line['value']
            if prop == 'T':
                self._add_isotherm_line(ax, value)
            elif prop == 'p':
                self._add_isobar_line(ax, value)
            elif prop == 'x':
                self._add_isoquality_line(ax, value)

        # draw points
        for point in self.points:
            v = 1 / point['rho']
            p = point['p']
            label = f'point (T = {round(point["T"],5)}, p = {p / 1e5})'
            ax.scatter(v, p / 1e5, label=label)
        # p_points = np.array([point['p'] for point in self.points])
        # v_points = 1 / np.array([point['rho'] for point in self.points])
        # ax.scatter(v_points, p_points / 1e5, label='points', c='g')

        ax.set_title(f'p-v Chart of {self.fluid}')
        # ax.set_ylim(bottom=0)

        plt.xlabel('specific Volume v [m^3/kg]')
        plt.ylabel('Pressure p [bar]')

        # ax.set_yscale('log')
        # ax.set_xscale('log')
        ax.set_xlim([0,0.05])

        plt.legend(loc='best')

        if show:
            fig.show()
        return fig

    def show(self):
        fig = self.figure
        fig.show()

    def add_point(self, T=None, p=None, x=None):
        if p is not None:
            p = p * 1e5
        if x is not None:
            if p is not None:
                T = PropsSI("T", "P", p, "Q", x, self.fluid)
                rho = PropsSI("D", "P", p, "Q", x, self.fluid)
            elif T is not None:
                p = PropsSI("P", "T", T, "Q", x, self.fluid)
                rho = PropsSI("D", "T", T, "Q", x, self.fluid)
            else:
                raise Exception('T or p have to be defined if x is defined')
        else:
            x = PropsSI("Q", "T", T, "P", p, self.fluid)
            rho = PropsSI("D", "T", T, "P", p, self.fluid)
        point = {'T': T, 'p': p, 'x': x, 'rho': rho}
        self.points.append(point)

    def add_iso_line(self, property='T', value: float = 200):
        props = ['T', 'p', 'v', 'x']

        if property not in ['T', 'p', 'v', 'x']:
            raise ValueError(f'property must be a string of {props}')

        if property == 'p':
            value = value * 1e5

        self.iso_lines.append({'property': property, 'value': value})


if __name__ == "__main__":
    pv_c = PvChart()
    pv_c.add_point(T=300, p=100)
    pv_c.add_iso_line('T', 300)
    pv_c.add_point(T=300, p=20)
    pv_c.add_iso_line('p', 20)
    [pv_c.add_iso_line('x', round(x,1)) for x in np.linspace(0.2, 0.8, 4)]
    pv_c.add_point(p=20, x=0.2)
    pv_c.show()
