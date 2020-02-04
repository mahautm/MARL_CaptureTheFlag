from gym.envs.registration import register

register(
    id='CtF-v0',
    entry_point='gym_CtF.envs:CtFEnv',
)
''' register(
    id='foo-extrahard-v0',
    entry_point='gym_foo.envs:FooExtraHardEnv',
) '''