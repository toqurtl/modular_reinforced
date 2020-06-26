from modular_reinforced.core.simulator import MesaModel
from config import Config
import os

EPISODES = 10
abs_path = os.path.dirname(os.path.realpath('.'))
data_path = os.path.join(abs_path, "sample_data")
cfg_file_path = os.path.join(data_path, "default.cfg")

with open(cfg_file_path, 'r') as f:
    cfg = Config(f)

sample_model = MesaModel(data_path, cfg)
sample_model.simulate_episode()


