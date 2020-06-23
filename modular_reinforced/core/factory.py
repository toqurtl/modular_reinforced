from mesa.agent import Agent
from modular_reinforced.core.element import UnitType, Unit
import logging


class FactoryAgent(Agent):
    def __init__(self, model):
        super().__init__('factory_1', model)
        self.log = logging.getLogger(self.unique_id)
        if not self.log.handlers:
            self.log.setLevel(logging.INFO)
            self.log.addHandler(logging.StreamHandler())
        self.production_schedule = []

    def product_unit(self, unit_type):
        unit = Unit(unit_type, self.model)
        self.model.inventory.add_unit(unit)
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' +self.unique_id \
                      + ':: product '+ str(unit))

    def register_production(self, unit_type):
        self.model.register_event(self.product_unit, unit_type, 3)
        type_name, _ = unit_type.value
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id \
                      +':: production start '+ type_name)

    def step(self):
        if self.model.time_step % 10 == 5:
            self.register_production(UnitType.A)
        elif self.model.time_step % 10 == 0:
            self.register_production(UnitType.B)
        return

