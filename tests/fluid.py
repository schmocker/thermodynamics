from tt.state import Fluid


f1 = Fluid()
f1 = Fluid(fluid='Water', **{'T': 300, 'p': 20*1E5})
print(f1.T)
f2 = f1.process_isobar_to('x', 0.5)

# f1.plot_pv()
# f2.plot_pv()


pass