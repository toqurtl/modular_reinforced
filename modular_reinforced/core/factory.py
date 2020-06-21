from mesa.agent import Agent
from modular_reinforced.core.element import UnitType


class FactoryAgent(Agent):
    def __init__(self, model):
        super().__init__('factory_1', model)
        self.production_schedule = []

    def product_unit(self, unit):
        self.model.inventory.add_unit(unit)
        print(self.unique_id,': product', unit)

    def register_production(self, unit):
        self.model.register_event(self.product_unit, unit, 3)
        print(self.unique_id,' production start', unit)

    def step(self):
        if self.model.time_step % 7 == 0:
            self.register_production(UnitType.A)
        elif self.model.time_step % 7 == 3:
            self.register_production(UnitType.B)
        else:
            pass
