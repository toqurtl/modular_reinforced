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
        # self.schedule.add(self.factory)

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

    @property
    def episode_finished(self):
        finished = True
        for site_agent in self.site_schedule.agents:
            if not site_agent.project_finished:
                finished = False
                break
        return finished

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
        self.factory.step()
        self.site_schedule.step()
        self.schedule.step()
        self.execute_event()

    # for reinforcement learning
    def action(self, unit_type):
        if unit_type is not None:
            self.factory.register_production(unit_type)

    def state(self):
        # number of inventory units, required unit for site, remained duration
        # number of inventory units
        print(str(self.time_step) + '=====================')
        print(self.inventory.num_unit_per_type())
        # required unit for site
        for site_agent in self.site_schedule.agents:
            print(site_agent.unit_schedule[site_agent.unit_schedule_index])
            print(site_agent.remaining_planned_duration)

        pass

