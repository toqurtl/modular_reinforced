import gym
from gym import error, spaces, utils
from gym.utils import seeding


class TestEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_list = []
        self.score = 0

    @property
    def action_size(self):
        return self.model.action_size

    @property
    def state_size(self):
        return len(self.model.state())


    def set_model(self, model):
        self.model = model
        self.model.reinforcement_env = True

    def step(self, action):
        self.action_list.append(action)
        next_state, reward, done = self.model.next(action)
        return next_state, reward, done

    def result_of_episode(self):
        finished_time_step, inventory_total, score = self.model.time_step, self.model.inventory_total, self.score
        return finished_time_step, inventory_total, score

    def reset(self):
        self.model.reset()
        self.action_list.clear()
        self.score = 0
        return self.model.state()

    # def render(self, mode='human', close=False):
    #     pass