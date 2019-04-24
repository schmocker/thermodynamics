from tt.fluid_state import Fluid, Process, ThermoChart

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