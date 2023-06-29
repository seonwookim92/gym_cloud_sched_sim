from gym.envs.registration import register

register(
    id='CloudSchedSim-v0',
    entry_point='gym_cloud_sched_sim.envs:CloudSchedSimEnv',
)