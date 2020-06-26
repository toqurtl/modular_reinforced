from mesa.agent import Agent
from modular_reinforced.core.element import Unit
import logging
import numpy as np


class FactoryAgent(Agent):
    def __init__(self, model):
        super().__init__('factory_1', model)
        self.log = logging.getLogger(self.unique_id)
        self.unit_type_info_dict = self.model.unit_type_info_dict
        if not self.log.handlers:
            self.log.setLevel(logging.INFO)
            self.log.addHandler(logging.StreamHandler())
        self.production_schedule = []
        self.unit_type_info_dict = model.unit_type_info_dict

    # Event: product unit
    def product_unit(self, type_idx):
        type_info = self.unit_type_info_dict.get(type_idx)
        unit = Unit(self.model, **type_info)
        self.model.inventory.add_unit(unit)
        # self.logging_production_finished(unit)

    # Event register:
    def register_production(self, type_idx):
        if type_idx == 0:
            pass
            # self.logging_factory_idle()
        else:
            self.model.register_event(self.product_unit, type_idx, 3)
            # self.logging_production_start(type_idx)

    # for logging
    def logging_production_start(self, type_idx):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id \
                      + ':: production start ' + str(type_idx))

    def logging_production_finished(self, unit):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id \
                      + ':: product ' + str(unit))

    def logging_factory_idle(self):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + 'production idle')

    # not use in reinforcement learning
    def step(self):
        if not self.model.reinforcement_env:
            if self.model.time_step % 10 == 5:
                self.register_production(1)
            elif self.model.time_step % 10 == 0:
                self.register_production(2)
        return

