from gym.envs.registration import register

register(
    id='test_env-v0',
    entry_point='modular_reinforced.reinforcement:TestEnv',
)