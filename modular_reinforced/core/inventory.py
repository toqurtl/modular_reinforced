from mesa.agent import Agent
from modular_reinforced.core.element import UnitType
import logging
import random

random.seed(1)


class InventoryAgent(Agent):
    def __init__(self, model):
        super().__init__('inven_1', model)
        self.log = logging.getLogger(self.unique_id)
        if not self.log.handlers:
            self.log.setLevel(logging.INFO)
            self.log.addHandler(logging.StreamHandler())

        self.inventory = {
            UnitType.A: [],
            UnitType.B: []
        }
        self.capacity = 100000

        self.request_dict_in_step = {}
        self.request_from_sites_list = []
        self.num_trailer = 5
        self.trailer_capacity = 1


    @property
    def num_unit(self, unit_type):
        return len(self.inventory[unit_type])

    def num_unit_per_type(self):
        num_unit_list = []
        for unit_type in self.inventory.keys():
            num_unit_list.append(len(self.inventory[unit_type]))
        return num_unit_list

    def __inventory_str(self):
        return_str = ''
        for key, value in self.inventory.items():
            type_name, _ = key.value
            return_str += type_name + ': ' + str(len(value)) + ', '
        return return_str

    def register_deliver(self, args):
        site, unit = args[0], args[1]
        site.units_in_the_site['wait'].append(unit)
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' \
                      + site.unique_id + ':: arrived new unit ' + str(unit))

    # args: site_agent, unit
    def delivery_to_site(self, *args):
        site, unit_type = args[0], args[1]
        if len(self.inventory[unit_type]) > 0:
            unit = self.inventory[unit_type][0]
            self.model.register_event(self.register_deliver, [site, unit], 3)
            self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id +'::' \
                    + str(unit) + ' start to move to ' + site.unique_id)
            self.inventory[unit_type].remove(unit)
            self.request_from_sites_list.remove(args)
            return
        else:
            return

    def get_unit(self, unit_type):
        if len(self.inventory[unit_type]) > 0:
            return self.inventory[unit_type][0]
        else:
            return None

    def delivery(self):
        check = 0
        for site, unit_type in self.request_from_sites_list:
            if check < 5:
                self.delivery_to_site(site, unit_type)
            check += 1

    def add_unit(self, unit):
        self.inventory[unit.type].append(unit)

    def print_state(self):
        self.log.info('t_' + str(self.model.time_step) + '::STATUS::' + self.unique_id + '::' \
                      + 'storage status is '+ self.__inventory_str())

    def step(self):
        self.print_state()
        self.delivery()
        random.shuffle(self.request_from_sites_list)
        # self.log.info('t_' + str(self.model.time_step) + '::STATUS::' + self.unique_id + \
        #               ':: # of request_list: ' + str(len(self.request_from_sites_list)))

