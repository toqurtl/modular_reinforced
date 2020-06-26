import gym
import json
import os
from config import Config
from modular_reinforced.core.simulator import MesaModel
from modular_reinforced.reinforcement.dqn import DQNAgent
import numpy as np

# import unit information for simulation
with open("sample_data/unit_info.json", "r") as unit_info_file:
    unit_type_info_dict = json.load(unit_info_file)

# import site information for simulation
with open("sample_data/site_info.json", "r") as site_info_file:
    site_info_list = json.load(site_info_file).get("sites")

abs_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(abs_path, "sample_data")
cfg_file_path = os.path.join(data_path, "default.cfg")
with open(cfg_file_path, 'r') as f:
    cfg = Config(f)

sample_model = MesaModel(data_path, cfg)

env = gym.make('test_env-v0')
env.set_model(sample_model)
agent = DQNAgent(env.state_size, env.action_size)

EPISODES = 100
scores, episodes = [], []
for e in range(EPISODES):
    done = False
    score = 0
    state = env.reset()
    state = np.reshape(state, [1, env.state_size])
    while not done:
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)
        next_state = np.reshape(next_state, [1, env.state_size])
        agent.append_sample(state, action, reward, next_state, done)
        if len(agent.memory) >= agent.train_start:
            agent.train_model()
        state = next_state
        # score += reward

        if done:
            agent.update_target_model()
            finished_time_step = env.model.time_step

            # score = score if score == 500 else score + 100

            scores.append(score)
            episodes.append(e)
            print("episode:", e, "  finished:", finished_time_step, " inven_total", env.model.inventory_total,
                  "  memory length:", len(agent.memory), "  epsilon:", agent.epsilon)

            # if np.mean(scores[-min(10, len(scores)):]) > 490:
            #     agent.model.save_weights("./save_model/cartpole_dqn.h5")
            #     sys.exit()


