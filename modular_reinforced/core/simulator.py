from mesa import Agent, Model
from mesa.time import BaseScheduler
from modular_reinforced.core.inventory import InventoryAgent
from modular_reinforced.core.factory import FactoryAgent
import modular_reinforced.core.utils as utils


class MesaModel(Model):
    def __init__(self, max_site, max_step):
        self.schedule = BaseScheduler(self)
        self.site_schedule = BaseScheduler(self)
        self.inventory = InventoryAgent(self)
        self.factory = FactoryAgent(self)
        self.schedule.add(self.inventory)
        self.schedule.add(self.factory)

        self.running = True

        self.max_site = max_site
        self.max_step = max_step

        # reserved event list (function, argument, execution time step)
        self.event_list = []

        self.site_id_generator = utils.site_id_generator()
        self.unit_id_generator = utils.unit_id_generator()

    def register_event(self, func, args, time_interval):
        self.event_list.append((func, args, time_interval + self.time_step))

    def execute_event(self):
        for func, args, time_step in self.event_list:
            if time_step == self.time_step:
                func(args)

    @property
    def num_site(self):
        return len(self.site_schedule.agents)

    @property
    def time_step(self):
        return self.schedule.steps

    def add_site_agent(self, site_agent):
        if len(self.site_schedule.agents) >= self.max_site:
            print('number of site_list have to be smaller than max site of the model')
            exit()
        else:
            self.site_schedule.add(site_agent)


    def site_state(self):
        for site in self.site_schedule:
            pass

    def site_state_with_idx(self, site_idx):
        site = self.site_schedule[site_idx]

    def print_previous_state(self):
        pass

    def print_after_step_state(self):
        pass

    def step(self):
        print('time:',self.time_step)

        self.site_schedule.step()
        self.schedule.step()
        self.execute_event()