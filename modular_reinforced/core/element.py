from mesa import Agent
from enum import Enum
import logging
import csv


class Unit(Agent):
    def __init__(self, model, **unit_info):
        unit_id = next(model.unit_id_generator)
        super().__init__(unit_id, model)
        self.unit_type = unit_info.get("unit_type")
        self.type_idx = unit_info.get("type_idx")
        self.install_duration = unit_info.get("install_duration")
        self.site_working = True
        self.installed = False
        # self.location = Location.Factory
        self.install_start_step = 0

    def __str__(self):
        return self.unique_id +'('+str(self.type_idx) +')'

    @property
    def duration(self):
        return self.install_duration

    @property
    def install_finish_step(self):
        return self.install_start_step + self.install_duration

    @property
    def remained_duration(self):
        return self.install_finish_step - self.model.step

    def step(self):
        if self.site_working:
            if self.remained_duration == 0:
                self.installed = True

