import json
import gym
import os
from config import Config
from modular_reinforced.core.simulator import MesaModel
from modular_reinforced.reinforcement.dqn import DQNAgent
import numpy as np
from matplotlib import pyplot as plt


abs_path = os.path.dirname(os.path.realpath('.'))
data_path = os.path.join(abs_path, "sample_data")
cfg_file_path = os.path.join(data_path, "default.cfg")
with open(cfg_file_path, 'r') as f:
    cfg = Config(f)

sample_model = MesaModel(data_path, cfg)

env = gym.make('test_env-v0')
env.set_model(sample_model)
agent = DQNAgent(env.state_size, env.action_size)

EPISODES = 1000
score_list, finished_duration_list, inven_total_list, episodes = [], [], [], []
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
        score += reward

        if done:
            agent.update_target_model()
            finished_time_step = env.model.time_step
            inven_total = env.model.inventory_total
            score_list.append(score)
            inven_total_list.append(inven_total)
            finished_duration_list.append(finished_time_step)
            episodes.append(e)
            # print("episode:", e, "  finished:", finished_time_step, " inven_total", inven_total,
            #       "  memory length:", len(agent.memory), "  epsilon:", agent.epsilon)
            print("episode:", e, "  finished:", finished_time_step, " inven_total", inven_total,
                  "score", score)
            print(env.action_list)


            # if np.mean(scores[-min(10, len(scores)):]) > 490:
            #     agent.model.save_weights("./save_model/cartpole_dqn.h5")
            #     sys.exit()
agent.model.save_weights("sample_model_weight.h5")
plt.plot(episodes, score_list)
plt.plot(episodes, finished_duration_list)
plt.plot(episodes, inven_total_list)
plt.show()
plt.savefig("result.png")
result = np.array([score_list, finished_duration_list, inven_total_list, episodes])
np.savetxt("result.csv", result, delimiter=",")


