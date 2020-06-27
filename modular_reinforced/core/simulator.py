from mesa import Agent, Model
from mesa.time import BaseScheduler
from modular_reinforced.core.inventory import InventoryAgent
from modular_reinforced.core.factory import FactoryAgent
from modular_reinforced.core.site import SiteAgent
import modular_reinforced.core.utils as utils
import numpy as np
import json
import os
from random import randint


class MesaModel(Model):

    def __init__(self, data_path, cfg):
        # get required information from cfg
        self.cfg = cfg
        self.max_site = int(cfg.max_num_of_site)
        self.max_step = int(cfg.max_step)
        self.unit_info_path = os.path.join(data_path, cfg.unit_json_file_path)
        self.site_info_path = os.path.join(data_path, cfg.site_json_file_path)

        # get component information from json
        self.unit_type_info_dict = {}
        self.site_agent_list = []
        self.__read_component_from_json()
        self.target_num = {}
        # baseline for simulation
        self.inventory = InventoryAgent(self)
        self.factory = FactoryAgent(self)
        self.reinforcement_env = False
        self.__initialize()

        # save_result
        self.inventory_result = []
        self.site_result = []

    def __initialize(self):
        self.site_schedule = BaseScheduler(self)
        self.schedule = BaseScheduler(self)
        self.event_list = [] # reserved event list (function, argument, execution time step)
        self.constructed_unit_list = []
        self.unit_id_generator = utils.unit_id_generator()
        self.__scheduling_site_agents()

        # final result
        self.finished_time_step = 0
        self.inventory_total = 0

        # for reinforcement_learning
        self.reward_at_time_step = 0

    # for initialization
    def reset(self):
        self.__initialize()
        self.factory.reset()
        self.inventory.reset()
        for site_agent in self.site_agent_list:
            site_agent.reset()

    def __read_component_from_json(self):
        with open(self.unit_info_path, "r") as unit_info_file:
            unit_type_info_list = json.load(unit_info_file).get("unit_types")
            for unit_type_info in unit_type_info_list:
                key = unit_type_info.get("type_idx")
                self.unit_type_info_dict[key] = unit_type_info

        with open(self.site_info_path, "r") as site_info_file:
            site_info_list = json.load(site_info_file).get("sites")

        for site_info in site_info_list:
            self.site_agent_list.append(SiteAgent(self, **site_info))

    def __scheduling_site_agents(self):
        for site_agent in self.site_agent_list:
            self.site_schedule.add(site_agent)

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
    def state_space(self):
        return

    def get_remained_site_unit(self, type_idx):
        count = 0
        if type_idx == 0:
            count = 1
        else:
            for site_agent in self.site_agent_list:
                count += list(site_agent.unit_schedule).count(type_idx)
        return count

    def step(self):
        self.reward_at_time_step = 0
        self.schedule.step()
        self.factory.step()
        self.site_schedule.step()
        self.inventory.step()
        self.execute_event()

    # for reinforcement learning
    @property
    def action_size(self):
        return len(self.unit_type_info_dict.items()) + 1

    def state(self):
        #TODO -
        factory_state = [self.get_remained_site_unit(1), self.get_remained_site_unit(2)]
        inven_state = self.inventory.num_unit_per_type()
        site_state = []
        for site_agent in self.site_schedule.agents:
            site_state += site_agent.get_state()
        state = factory_state + inven_state + site_state
        return np.array(state)

    def next(self, action):
        # type_idx = randint(1,2)
        if self.reinforcement_env:
            self.factory.register_production(action)
            self.factory.production_schedule.append(action)
        if self.get_remained_site_unit(action) == 0:
            self.reward_at_time_step -= 1000

        self.step()
        return self.state(), self.reward(), self.episode_finished

    def reward(self):
        return self.reward_at_time_step

    def simulate_episode(self):
        while not self.episode_finished:
            self.step()
            if self.episode_finished:
                for site in self.site_agent_list:
                    if 20 > site.remaining_planned_duration > 0:
                        self.reward_at_time_step += 1000
                    elif 40 > site.remaining_planned_duration >= 20:
                        self.reward_at_time_step += 2000




