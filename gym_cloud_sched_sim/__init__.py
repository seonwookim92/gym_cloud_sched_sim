from gym.envs.registration import register

register(
    id='CloudSchedSim-v0',
    entry_point='envs:CloudSchedSimEnv',
)