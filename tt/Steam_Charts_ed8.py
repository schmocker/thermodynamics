import CoolProp
from CoolProp.CoolProp import PropsSI
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as patches


Tc = PropsSI("Tcrit", "Water")
Pc = PropsSI("Pcrit", "Water") 

# need to make change if state is saturated....

class SteamCharts:
    '''information regarding the pump and turbine conditions are stored
    here including the isentropic efficiencies'''

    def __init__(self, t_steam, p_steam): # t in °C, p in bar
        self.T = t_steam + 273.15
        self.p = p_steam * 1e5
        self.saturated = 'False'
        if self.p < Pc:
            self.T1_sat = PropsSI("T","P",self.p,"Q",0,"HEOS::Water")
            if abs(self.T-self.T1_sat) < 0.2:
                self.saturated = 'True'
        else:
            self.T1_sat = Tc - 10

        if self.T < Tc:
            self.p1_sat = PropsSI("P","T",self.T,"Q",0,"HEOS::Water")
        else:
            self.p1_sat = Pc - 10

        T_diff = self.T - self.T1_sat # overheat or undercool
        p_diff = self.p - self.p1_sat # overpress or underpress
        if T_diff > 0:
            self.T_over = 75
        else:
            self.T_over = -T_diff + 75
        if T_diff < 0:
            self.T_under = T_diff -20
        else:
            self.T_under = -20

        if p_diff > 0:
            self.p_over = p_diff + self.p * 0.4
        else:
            self.p_over = self.p1_sat + 0.4 * self.p
        if p_diff < 0:
            self.p_under = p_diff - 0.2 * self.p
        else:
            self.p_under = -p_diff - 0.2 * self.p    
        
    def T_v_plot(self):
        Temps = np.linspace(self.T1_sat + self.T_under, self.T + self.T_over,200)
        fig = plt.figure()
        # plotting the isobar in T_v diagram
        plt.semilogx(1/PropsSI("D","P",self.p,"T",Temps,"HEOS::Water"), Temps, label = 'Pressure = '+ str(self.p/1e5)+ ' bar, ')
        if self.saturated == 'False':
            plt.semilogx(1/PropsSI("D","P",self.p,"T",self.T,"HEOS::Water"), self.T, 'ro', \
                     label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
        else:
            v = float(input('The state is saturated. Enter the speoific volume in m^3/kg '))
            plt.semilogx(v, self.T, 'ro', label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
                
    
        # plotting the saturation states
        Tc = PropsSI("Tcrit", "Water")
        T_range = np.linspace(273.16, Tc, 200)
        V_liquid = 1/PropsSI("D","T",T_range,"Q",0,"HEOS::Water")
        V_vapor = 1/PropsSI("D","T",T_range,"Q",1,"HEOS::Water")
        plt.semilogx(V_liquid, T_range)
        plt.semilogx(V_vapor, T_range)

        plt.xlabel('specific Volume (v) in m^3/kg')
        plt.ylabel('Temperature [deg K]')
        plt.legend(loc = 'best')
        plt.show(block = False)

    def p_v_plot(self):
        Press = np.linspace(self.p + self.p_under, self.p + self.p_over,200)
        fig = plt.figure()
        # plotting the isotherm in P_v diagram
        plt.semilogx(1/PropsSI("D","P",Press,"T",self.T,"HEOS::Water"), Press/1e5, label = 'Temperature = '+ str(self.T)+ ' K, ')
        if self.saturated == 'False':
            plt.semilogx(1/PropsSI("D","P",self.p,"T",self.T,"HEOS::Water"), self.p/1e5, 'ro', \
                     label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
        else:
            v = float(input('The state is saturated. Enter the speoific volume in m^3/kg '))
            plt.semilogx(v, self.p/1e5, 'ro', label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
    
        # plotting the saturation states 
        P_range = np.logspace(np.log10(611), np.log10(Pc), 1000) # 611 is just above the triple point pressure
        V_liquid = 1/PropsSI("D","P",P_range,"Q",0,"HEOS::Water")
        V_vapor = 1/PropsSI("D","P",P_range,"Q",1,"HEOS::Water")
        plt.semilogx(V_liquid, P_range/1e5)
        plt.semilogx(V_vapor, P_range/1e5)
        plt.gca().set_ylim(bottom = 0) # had problems with neg. pressures when above critical pt

        plt.xlabel('specific Volume (v) in m^3/kg')
        plt.ylabel('Pressure [bar]')
        plt.legend(loc = 'best')
        plt.show(block = False)

    def logp_v_plot(self):
        Press = np.linspace(self.p + self.p_under, self.p + self.p_over,200)
        fig = plt.figure()
        # plotting the isotherm in P_v diagram
        plt.loglog(1/PropsSI("D","P",Press,"T",self.T,"HEOS::Water"), Press/1e5, label = 'Temperature = '+ str(self.T)+ ' K, ')
        if self.saturated == 'False':
            plt.loglog(1/PropsSI("D","P",self.p,"T",self.T,"HEOS::Water"), self.p/1e5, 'ro', \
                     label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
        else:
            v = float(input('The state is saturated. Enter the speoific volume in m^3/kg '))
            plt.loglog(v, self.p/1e5, 'ro', label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
    
        # plotting the saturation states 
        P_range = np.logspace(np.log10(611), np.log10(Pc), 1000) # 611 is just above the triple point pressure
        V_liquid = 1/PropsSI("D","P",P_range,"Q",0,"HEOS::Water")
        V_vapor = 1/PropsSI("D","P",P_range,"Q",1,"HEOS::Water")
        plt.loglog(V_liquid, P_range/1e5)
        plt.loglog(V_vapor, P_range/1e5)
        plt.gca().set_ylim(bottom = 0) # had problems with neg. pressures when above critical pt

        plt.xlabel('specific Volume (v) in m^3/kg')
        plt.ylabel('Pressure [bar]')
        plt.legend(loc = 'best')
        plt.show(block = False)
    
    def T_s_plot(self):
        Temps = np.linspace(self.T1_sat + self.T_under, self.T + self.T_over,200)
        fig = plt.figure()
        # plotting the isobar in T_s diagram
        plt.plot(PropsSI("Smass","P",self.p,"T",Temps,"HEOS::Water"), Temps, label = 'Pressure = '+ str(self.p/1e5)+ ' bar, ')
        if self.saturated == 'False':
            plt.plot(PropsSI("Smass","P",self.p,"T",self.T,"HEOS::Water"), self.T, 'ro', \
                     label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')
        else:
            s = float(input('The state is saturated. Enter the speoific entropy in J/(kg K) '))
            plt.plot(s, self.T, 'ro', label = 'P = '+ str(self.p/1e5)+ ' bar, ' + 'T = '+ str(self.T)+ ' K')

        # plotting the saturation states
        T_range = np.linspace(273.16, Tc, 200)
        S_liquid = PropsSI("S","T",T_range,"Q",0,"HEOS::Water")
        S_vapor = PropsSI("S","T",T_range,"Q",1,"HEOS::Water")
        plt.plot(S_liquid, T_range)
        plt.plot(S_vapor, T_range)

        plt.xlabel('specific Entropy (s) in J/(kg K)')
        plt.ylabel('Temperature [deg K]')
        plt.legend(loc = 'best')
        plt.show(block = False)

if __name__ == "__main__":
    sc = SteamCharts(300, 100)
    sc.p_v_plot()


