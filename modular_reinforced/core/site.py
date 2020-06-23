from mesa.agent import Agent
from modular_reinforced.core.element import UnitType
import logging
request_capacity = 1


class SiteAgent(Agent):
    def __init__(self, planned_duration, model, activate=False, unit_schedule=[]):
        site_id = next(model.site_id_generator)
        super().__init__(site_id, model)
        self.log = logging.getLogger(self.unique_id)
        if not self.log.handlers:
            self.log.setLevel(logging.INFO)
            self.log.addHandler(logging.StreamHandler())

        self.activate = activate
        # unit_schedule is unit_type list
        self.unit_schedule = unit_schedule
        self.unit_schedule_index = 0
        self.remained_unit_dict = {}

        self.is_working = False

        self.units_in_the_site = {
            'wait': [],
            'install': [],
            'finish': []
        }

        self.planned_duration = planned_duration
        self.installed_unit = []
        self.arrived_unit = []

        self.logistic_interval = 4

        self.working_unit = None

        self.is_request = False

        for unit_type in unit_schedule:
            if unit_type in self.remained_unit_dict.keys():
                self.remained_unit_dict[unit_type] += 1
            else:
                self.remained_unit_dict[unit_type] = 1

    @property
    def project_finished(self):
        return len(self.unit_schedule) == self.unit_schedule_index

    @property
    def __is_working(self):
        return len(self.units_in_the_site['install']) == 0

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
        for key, value in self.remained_unit_dict.items():
            type_name, _ = key.value
            return_str += type_name + ': ' + str(value) + ', '
        return return_str

    def get_unit_from_arrived(self, unit_type):
        selected_unit = None
        for unit in self.units_in_the_site['wait']:
            if unit.type == unit_type:
                selected_unit = unit
                break
        if selected_unit is not None:
            self.units_in_the_site['wait'].remove(unit)
        return selected_unit



    @property
    def requested_unit(self):
        # if the number of remained unit is smaller than request_capacity,
        if len(self.unit_schedule) > request_capacity:
            return self.unit_schedule[-request_capacity:]
        else:
            return self.unit_schedule

    def request_unit(self, unit):
        self.model.inventory.request_from_sites_list.append((self, unit))
        self.log.info('t_' + str(self.model.time_step) + '::EVENT::' + self.unique_id \
                      + '::request new unit to inventory')

    # if is_working and finished, request another
    def work(self):
        if self.is_working:
            if self.model.time_step == self.unit_work_finish_step:
                self.remained_unit_dict[self.working_unit.type] -= 1
                self.working_unit = None
                self.is_working = False
                self.is_request = False
                self.unit_schedule_index += 1
        else:
            request_unit_type = self.unit_schedule[self.unit_schedule_index]
            selected_unit = self.get_unit_from_arrived(request_unit_type)
            if selected_unit is not None:
                self.working_unit = selected_unit
                self.unit_work_start_step = self.model.time_step
                self.unit_work_finish_step = self.model.time_step + self.working_unit.duration
                self.is_working = True
            else:
                if not self.is_request:
                    self.request_unit(self.unit_schedule[self.unit_schedule_index])
                    self.is_request = True

    def print_state(self):
        self.log.info('t_' + str(self.model.time_step) + '::STATUS::' + self.unique_id + ':: working unit is ' \
                      + str(self.working_unit) + ' remained_unit is '+ self.__remained_unit_string())


    def step(self):
        if not self.project_finished:
            self.work()
            self.print_state()

