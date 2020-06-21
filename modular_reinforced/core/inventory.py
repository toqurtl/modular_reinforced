from mesa.agent import Agent
from modular_reinforced.core.element import UnitType


class InventoryAgent(Agent):
    def __init__(self, model):
        super().__init__('inven_1', model)

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

    def register_deliver(self, args):
        site, unit = args[0], args[1]
        site.arrived_unit.append(unit)
        print(site.unique_id, 'arrived new unit', unit)

    # args: site_agent, unit
    def delivery_to_site(self, *args):
        site, unit = args[0], args[1]
        if len(self.inventory[unit]) > 0:
            self.model.register_event(self.register_deliver, args, 3)
            print(unit, 'start to move to', site.unique_id)
            self.inventory[unit].remove(unit)
            return
        else:
            return

    def delivery(self):
        check = 0
        for site, unit in self.request_from_sites_list:
            if check < 5:
                self.delivery_to_site(site, unit)
            check += 1

    def add_unit(self, unit):
        self.inventory[unit].append(unit)

    def print_state(self):
        print(self.unique_id, 'storing', 'A', len(self.inventory[UnitType.A]), 'B', len(self.inventory[UnitType.B]))

    def step(self):
        self.print_state()
        self.delivery()
