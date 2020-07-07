import numpy as np
from random import randint


class Learner(object):
    def __init__(self, envs, **kwargs):
        self.envs = envs
        self.num_episode = kwargs.get('num_episode')
        data_collector = {
            'episode': [],
            'episode_info':[],
            'score': [],
            'finished_duration': [],
            'inventory_total': [],
            'production_schedule': []
        }

    def add_episode_result(self):
        pass

    def step(self):
        done = False
        score = 0
        state = self.env.reset()
        state = np.reshape(state, [1, self.env.state_size])
        site_1_start_step, site_2_start_step = randint(0, 50), randint(0, 50)
        self.episode_info.append([site_1_start_step, site_2_start_step])
        performance_good = False
        self.env.model.site_agent_list[0].start_time_step = site_1_start_step
        self.env.model.site_agent_list[1].start_time_step = site_2_start_step