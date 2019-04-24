from . import ureg, FluidState, AbstractFluid

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