import gym
from gym import error, spaces, utils
from gym.utils import seeding


class TestEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_list = []

    @property
    def action_size(self):
        return self.model.action_size

    @property
    def state_size(self):
        return 18

    def set_model(self, model):
        self.model = model
        self.model.reinforcement_env = True

    def step(self, action):
        self.action_list.append(action)
        next_state, reward, done = self.model.next(action)
        return next_state, reward, done

    def reset(self):
        self.model.reset()
        self.action_list.clear()
        return self.model.state()

    # def render(self, mode='human', close=False):
    #     pass