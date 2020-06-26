from mesa.agent import Agent
from collections import deque
import logging
import numpy as np


class SiteAgent(Agent):
    def __init__(self, model, **kwargs):

        super().__init__(kwargs.get("site_id"), model)
        self.log = logging.getLogger(self.unique_id)
        if not self.log.handlers:
            self.log.setLevel(logging.INFO)
            self.log.addHandler(logging.StreamHandler())

        # set site from cfg
        self.unit_schedule_origin = kwargs.get("unit_schedule")
        self.planned_duration = kwargs.get("planned_duration")
        self.start_time_step = kwargs.get("start_time_step")
        self.logistic_interval = kwargs.get("logistic_interval")
        self.request_condition_num_unit = kwargs.get("request_condition")

        # simulation
        self.units_in_the_site = {
            'wait': [],
            'install': [],
            'finish': []
        }
        self.remained_unit_dict = {}
        self.__initialize()

    def __initialize(self):
        # set remained_unit_dict
        self.unit_schedule = deque(self.unit_schedule_origin)
        self.request_unit_type = 0
        self.cost = 0
        for type_idx in self.model.unit_type_info_dict.keys():
            self.remained_unit_dict[type_idx] = 0

        for type_idx in self.unit_schedule_origin:
            if type_idx in self.remained_unit_dict.keys():
                self.remained_unit_dict[type_idx] += 1

        for unit_list in self.units_in_the_site.values():
            unit_list.clear()

    def reset(self):
        self.__initialize()

    @property
    def is_request(self):
        return self.request_unit_type != 0

    @property
    def request_condition(self):
        return len(self.units_in_the_site["wait"]) < self.request_condition_num_unit

    @property
    def project_started(self):
        return self.start_time_step <= self.model.time_step
    @property
    def project_finished(self):
        return len(list(self.unit_schedule)) == 0

    @property
    def is_working(self):
        return len(self.units_in_the_site['install']) != 0

    @property
    def working_unit(self):
        if self.is_working:
            return self.units_in_the_site['install'][0]
        else:
            return None

    @property
    def remaining_planned_duration(self):
        return self.planned_duration - self.model.time_step

    @property
    def start_step(self):
        return self.model.stie_schedule.steps

    @property
    def finish_step(self):
        return self.start_step + self.planned_duration

    def __remained_unit_string(self):
        return_str = ''
        for type_id, value in self.remained_unit_dict.items():
            return_str += str(type_id) + ': ' + str(value) + ', '
        return return_str

    def remained_unit_info(self):
        return list(self.remained_unit_dict.values())

    # check there is request unit. if there is, return selected_unit
    def get_unit_from_arrived(self):
        unit_arrived, selected_unit = False, None
        for unit in self.units_in_the_site['wait']:
            if unit.type_idx == self.request_unit_type:
                selected_unit, unit_arrived = unit, True
                break
        return unit_arrived, selected_unit

    def request_unit(self):
        self.model.inventory.request_from_sites_list.append((self, self.request_unit_type))

    def unit_to_wait(self, unit):
        self.units_in_the_site["wait"].append(unit)

    def unit_to_install(self):
        unit_arrived, selected_unit = self.get_unit_from_arrived()
        unit_moved = unit_arrived and not self.is_working
        if unit_moved:
            self.units_in_the_site["wait"].remove(selected_unit)
            self.units_in_the_site["install"].append(selected_unit)

        return unit_moved, unit_arrived

    def unit_to_finish(self):
        self.remained_unit_dict[self.working_unit.type_idx] -= 1
        self.units_in_the_site["install"].remove(self.working_unit)
        self.units_in_the_site["finish"].append(self.working_unit)
        self.request_unit_type=0
        # self.logging_install_finish()

    # if is_working and finished, request another
    def work(self):
        if self.is_working:
            # if finished, request new unit
            if self.model.time_step == self.unit_work_finish_step:
                self.unit_to_finish()

        else:
            # if request_condition(there are inefficient unit on wait state) and not request yet, request unit
            if self.request_condition and not self.is_request:
                self.request_unit_type = self.unit_schedule.popleft()
                if self.request_unit_type == 0:
                    self.log.debug('site_class:error')
                    exit()
                self.request_unit()

            # if not working, try to move wait unit to install
            unit_moved, unit_arrived = self.unit_to_install()
            if unit_moved:
                self.unit_work_start_step = self.model.time_step
                self.unit_work_finish_step = self.model.time_step + self.working_unit.duration
                # self.logging_install_start()

    def get_state(self):
        required_unit = [self.request_unit_type]
        remaining_planned_duration = [self.remaining_planned_duration]
        remained_unit_list = self.remained_unit_info()
        return required_unit + remaining_planned_duration + remained_unit_list

    # for logging
    def logging_state(self):
        self.log.info('t_' + str(self.model.time_step) + '::STATUS::' + self.unique_id + ':: working unit is ' \
                      + str(self.working_unit) + ' remained_unit is '+ self.__remained_unit_string())

    def logging_request(self):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id + '::request new unit to inventory')

    def logging_install_start(self):
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::'+ self.unique_id + ':: start installing in ' + self.unique_id)
        self.log.info('t_' + str(self.model.time_step) + '::EVENT:: it will finished at ' + str(self.unit_work_finish_step))

    def logging_install_finish(self):
        self.log.info(
            't_' + str(self.model.time_step) + '::EVENT::' + self.unique_id + ':: install finish')

    # step
    def step(self):
        if not self.project_finished and self.project_started:
            self.work()
            self.logging_state()

