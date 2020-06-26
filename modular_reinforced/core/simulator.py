from mesa import Agent, Model
from mesa.time import BaseScheduler
from modular_reinforced.core.inventory import InventoryAgent
from modular_reinforced.core.factory import FactoryAgent
from modular_reinforced.core.site import SiteAgent
import modular_reinforced.core.utils as utils
import numpy as np
import json
import os


class MesaModel(Model):
    def __init__(self, data_path, cfg):
        # get required information from cfg
        self.cfg = cfg
        self.max_site = int(cfg.max_num_of_site)
        self.max_step = int(cfg.max_step)
        unit_info_path = os.path.join(data_path, cfg.unit_json_file_path)
        site_info_path = os.path.join(data_path, cfg.site_json_file_path)
        self.unit_type_info_dict = {}
        with open(unit_info_path, "r") as unit_info_file:
            unit_type_info_list = json.load(unit_info_file).get("unit_types")
            for unit_type_info in unit_type_info_list:
                key = unit_type_info.get("type_idx")
                self.unit_type_info_dict[key] = unit_type_info

        with open(site_info_path, "r") as site_info_file:
            self.site_info_list = json.load(site_info_file).get("sites")

        # baseline for simulation
        self.schedule = BaseScheduler(self)
        self.site_schedule = BaseScheduler(self)
        self.inventory = InventoryAgent(self)
        self.factory = FactoryAgent(self)
        self.schedule.add(self.inventory)
        self.reinforcement_env = False
        self.__generate_site_agents()

        # simulation handlers
        # reserved event list (function, argument, execution time step)
        self.event_list = []
        self.unit_id_generator = utils.unit_id_generator()

    # for initialization
    def __generate_site_agents(self):
        for site_info in self.site_info_list:
            self.add_site_agent(SiteAgent(self, **site_info))

    # event managing function
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

    @property
    def action_space(self):
        return len(self.unit_type_info_dict.items())

    @property
    def state_space(self):
        return

    def add_site_agent(self, site_agent):
        if len(self.site_schedule.agents) >= self.max_site:
            print('number of site_list have to be smaller than max site of the model')
            exit()
        else:
            self.site_schedule.add(site_agent)

    def step(self):
        self.factory.step()
        self.site_schedule.step()
        self.schedule.step()
        self.execute_event()

    # for reinforcement learning
    def action(self, type_idx):
        self.factory.register_production(type_idx)

    def action_size(self):
        return len(self.unit_type_info_dict.list())

    def state(self):
        inven_state = self.inventory.num_unit_per_type()
        site_state = []
        for site_agent in self.site_schedule.agents:
            site_state += site_agent.get_state()
        state = inven_state + site_state
        return len(state), np.array(state)

    def simulate_episode(self):
        while not self.episode_finished:
            self.step()
