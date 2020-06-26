from mesa.agent import Agent
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

        # set inventory information
        self.__set_inventory()
        self.capacity = self.model.cfg.capacity
        self.num_trailer = self.model.cfg.num_trailer
        self.trailer_capacity = self.model.cfg.trailer_capacity

        # for simulation
        self.request_dict_in_step = {}
        self.request_from_sites_list = []

    def __set_inventory(self):
        self.inventory = {}
        for type_idx in self.model.unit_type_info_dict.keys():
            self.inventory[type_idx] = []

    @property
    def num_unit(self, type_idx):
        return len(self.inventory[type_idx])

    @property
    def num_request(self):
        return len(self.request_from_sites_list)

    def num_unit_per_type(self):
        num_unit_list = []
        for type_idx in self.inventory.keys():
            num_unit_list.append(len(self.inventory[type_idx]))
        return num_unit_list

    def get_unit(self, type_idx):
        if len(self.inventory[type_idx]) > 0:
            return self.inventory[type_idx][0]
        else:
            return None

    # event handler
    def register_deliver(self, args):
        site, unit = args[0], args[1]
        site.units_in_the_site['wait'].append(unit)
        # self.logging_delivery_finished(site, unit)

    # TODO - if decision maker representation in inventory required, have to split this functions
    # args: site_agent, unit_type_idx
    def delivery_to_site(self, *args):
        site, type_idx = args[0], args[1]
        if len(self.inventory[type_idx]) > 0:
            unit = self.inventory[type_idx][0]
            self.model.register_event(self.register_deliver, [site, unit], 3)
            # self.logging_delivery_start(site, unit)
            self.inventory[type_idx].remove(unit)
            self.request_from_sites_list.remove(args)
            return
        else:
            return

    def delivery(self):
        check = 0
        for site, type_idx in self.request_from_sites_list:
            if check < self.trailer_capacity:
                self.delivery_to_site(site, type_idx)
            check += 1

    def add_unit(self, unit):
        self.inventory[unit.type_idx].append(unit)

    # for logging
    def __inventory_str(self):
        return_str = ''
        for type_idx, unit_list in self.inventory.items():
            return_str += str(type_idx) + ': ' + str(len(unit_list)) + ', '
        return return_str

    def logging(self):
        self.log.info('t_' + str(self.model.time_step) + '::STATUS::' + self.unique_id + '::' \
                      + 'storage status is '+ self.__inventory_str())
        # self.log.info('t_' + str(self.model.time_step) + '::STATUS::' + self.unique_id + \
        #               ':: # of request_list: ' + str(len(self.request_from_sites_list)))

    def logging_delivery_finished(self, site, unit):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' \
                      + site.unique_id + ':: arrived new unit ' + str(unit))

    def logging_delivery_start(self, site, unit):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id + '::' \
                      + str(unit) + ' start to move to ' + site.unique_id)
    # step
    def step(self):
        self.delivery()
        random.shuffle(self.request_from_sites_list)
        # self.logging()



