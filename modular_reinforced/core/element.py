from mesa import Agent
from enum import Enum
import logging
import csv


# type = duration in site
class UnitType(Enum):
    A = 3
    B = 4

    @classmethod
    def get_type(cls, unit_type):
        if unit_type == 'A':
            return cls.A
        elif unit_type == 'B':
            return cls.B
        else:
            print('There is no enum equal to unit type' + unit_type)
            return

    @classmethod
    def name(cls, unit_type_enum):
        if unit_type_enum == cls.A:
            return 'A'
        elif unit_type_enum == cls.B:
            return 'B'
        else:
            print('There is no enum equal to unit type_enum')
            return


class Location(Enum):
    Factory = 0
    Inventory = 1
    Delivery = 2
    Site = 3


class Unit(Agent):
    def __init__(self, unit_type_enum, model):
        unit_id = next(model.unit_id_generator())
        super().__init__(unit_id, model)
        self.type = unit_type_enum
        self.site_working = True
        self.installed = False
        self.location = Location.Factory
        self.install_start_step = 0

    def __str__(self):
        return UnitType.name(self.type)

    @property
    def duration(self):
        return self.type.value

    @property
    def install_finish_step(self):
        return self.install_start_step + self.duration

    @property
    def remained_duration(self):
        return self.install_finish_step - self.model.step

    def step(self):
        if self.site_working:
            if self.remained_duration == 0:
                self.installed = True

