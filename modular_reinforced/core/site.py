from mesa.agent import Agent

request_capacity = 1


class SiteAgent(Agent):
    def __init__(self, expected_duration, model, activate=False, unit_schedule=[]):
        site_id = next(model.site_id_generator)
        super().__init__(site_id, model)
        self.activate = activate
        self.unit_schedule = unit_schedule
        self.is_working = False
        self.remained_unit_dict = {}
        self.expected_duration = expected_duration
        self.installed_unit = []
        self.arrived_unit = []

        self.logistic_interval = 4

        self.working_unit = None

        for unit in unit_schedule:
            if unit in self.remained_unit_dict.keys():
                self.remained_unit_dict[unit] += 1
            else:
                self.remained_unit_dict[unit] = 1

    @property
    def project_finished(self):
        return len(self.unit_schedule) == 0

    @property
    def start_step(self):
        return self.model.stie_schedule.steps

    @property
    def finish_step(self):
        return self.start_step + self.expected_duration

    @property
    def requested_unit(self):
        # if the number of remained unit is smaller than request_capacity,
        if len(self.unit_schedule) > request_capacity:
            return self.unit_schedule[-request_capacity:]
        else:
            return self.unit_schedule

    def request_unit(self, unit):
        self.model.inventory.request_from_sites_list.append((self, unit))

    # if is_working and finished, request another
    def work(self):
        if self.is_working:
            if self.model.time_step == self.unit_work_finish_step:
                self.remained_unit_dict[self.working_unit] -= 1
                self.working_unit = None
                self.is_working = False
        else:
            if self.unit_schedule[0] in self.arrived_unit:
                self.working_unit = self.unit_schedule[0]
                self.arrived_unit.remove(self.working_unit)
                self.unit_work_start_step = self.model.time_step
                self.unit_work_finish_step = self.model.time_step + self.working_unit.value
                self.is_working = True
            else:
                self.request_unit(self.unit_schedule[0])

    def print_state(self):
        print(self.unique_id, '- working unit:', self.working_unit, end=' ')
        print('remained_unit:', self.remained_unit_dict)

    def step(self):
        self.work()
        self.print_state()