import gym
from gym_CtF.envs.flag import Flag
from gym_CtF.envs.agent import Agent

import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding

"""
    Description:
    A random map is generated with obstacles. 
    Two teams of agents are generated on opposite sides of the map.
    They each must capture the other team's flag without being killed by their opponent.
    First team to capture a flag wins.

    Observation:  (//!! has been modified)
      Type: Box(x*x*self.nbTeamMembers*4)
      each agent has 4 x*x sized maps for :
      Num	Action
        0 shows all surrounding positions, 0 being unblocked position and 1 indicating a blocked postion
        1 shows flags in surrounding positions, 0 meaning no flag, and 1 meaning flag
        2 shows friendly agents in surrounding positions, 0 meaning no friend, 1 meaning a friend is on the position
        3 shows ennemy agents in surrounding positions, 0 meaning no ennemy, 1 meaning a ennemy is on the position
        
    Actions: (//!! has been modified)
      Type: Box(2 * self.nbTeamMembers * 5) 
      For each team member, in each team:
      Num	Action
        0	  move left
        1	  move right
        2	  move up
        3	  move down
        4   attack
        
    Reward:
      WIP
    Starting State:
      WIP
    Episode Termination:
      WIP
"""


class CtFEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        # There shall be two teams to begin with
        self.nbTeamMembers = 5
        self.observation_size = 7
        # This is what the agents will be allowed to see each turn --> The observation space
        # Documentation hardly exists,
        # from reading the code I'll just align binary, event if that seems like a sub-optimal solution
        # self.observation_space = spaces.Box(
        #     low=0,
        #     high=1,
        #     # //!!\\ Temporary fix :
        #     # openAI baselines don't like multi dimensional input spaces so we're attempting 1d which will be hell to interpret.
        #     # should revert asap
        #     shape=(
        #         self.observation_size
        #         * self.observation_size
        #         * self.nbTeamMembers
        #         * 2
        #         * 4,
        #     ),
        #     dtype=np.int64,
        # )

        self.observation_space = spaces.MultiBinary(
            self.observation_size * self.observation_size * self.nbTeamMembers * 2 * 4
        )

        # self.action_space = spaces.Box(
        #     low=0, high=1, shape=(2 * self.nbTeamMembers * 5,), dtype=np.int64
        # )
        self.action_space = spaces.MultiBinary(2 * self.nbTeamMembers * 5)

        self.np_random = None
        self.seed()
        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        # checkups for data structure
        assert self.action_space.contains(action), "%r (%s) invalid" % (
            action,
            type(action),
        )

        self.state = []
        self.rewards = []

        for agentNb in range(len(self.agents)):
            self.agents[agentNb].move(action[agentNb * 5 : agentNb * 5 + 4], self.map)
            if action[agentNb * 5 + 4] == 1:
                self.agents[agentNb].attack(self.map, self.agents, self.flags)

            self.state = np.append(
                self.state,
                self.agents[agentNb].sight(self.map, self.flags, self.agents),
            )
            # //!! Beware, here the reward is set individually. No team reward is assigned !!\\
            self.agents[agentNb].updateReward(self.flags, self.agents)
            rew = self.agents[agentNb].reward
            self.rewards = np.append(self.rewards, rew)
            # for now rewards are only assigned on victory, no heuristics
            if rew == 1000:
                self.done = True
        # Optionally we can pass additional info, we are not using that for now
        info = {}

        # //!!\\ Temporary fix :
        # To use the baseline, their must be ONE SINGLE REWARD. This is not good to train 10 different models
        reward = np.sum(self.rewards)
        return self.state, reward, self.done, info

        # returns, in order, the state, the reward, and wether the game is over
        # return self.state, self.rewards, self.done, info

        # In agents there should be a table per agent, and inside that movement, then other actions

    def reset(self):
        self.done = False
        self.map = self.generateMap(100, 40)
        self.rewards = np.zeros(self.nbTeamMembers * 2)
        self.state = self.observation_space.sample()
        self.steps_beyond_done = None
        # There might come a time where teams are generated in a locked space
        # There will be a small probability of this happening.
        # It might later be dealt with by allowing interactions with environment
        self.agents = np.array([])
        self.flags = np.array([])

        # First team Flag is built
        self.flags = np.append(self.flags, Flag(1, 1, 1))
        # A flag, unlike a wall, can share its space, we remove walls on this location
        self.map[1][1] = False

        # First team members are assigned starting position in top left corner
        for i in range(self.nbTeamMembers):
            # positioned so as to be spaced by one from each other
            self.agents = np.append(
                self.agents, Agent((i + 1) * 2, 2, 1, self.observation_size)
            )
            # We add a Wall : You wannot walk on an agent
            self.map[2][(i + 1) * 2] = True

        #  Same for second Flag and team members, in bottom right corner
        self.flags = np.append(
            self.flags, Flag(len(self.map[0]) - 2, len(self.map) - 2, 2)
        )
        self.map[len(self.map) - 2][len(self.map[0]) - 2] = False
        for i in range(self.nbTeamMembers):
            self.agents = np.append(
                self.agents,
                Agent(
                    len(self.map[0]) - (i + 2) * 2,
                    len(self.map) - 3,
                    2,
                    self.observation_size,
                ),
            )
            self.map[len(self.map) - 3][len(self.map[0]) - (i + 2) * 2] = True

        return np.array(self.state)

    def render(self, mode="console"):
        if mode != "console":
            raise NotImplementedError()
        print(self.toStringMap(self.map))

    def close(self):
        # no idea what this does, just going with the flow here
        pass

    def mapCountAliveNeighbours(self, map, x, y):
        count = 0
        for i in range(3):
            for j in range(3):
                neighbour_x = x + j - 1
                neighbour_y = y + i - 1
                # In case the index we're looking off the edge of the map
                if (
                    neighbour_x < 0
                    or neighbour_y < 0
                    or neighbour_y >= len(map)
                    or neighbour_x >= len(map[0])
                ):
                    count += 1
                # Otherwise, a normal check of the neighbour
                elif map[neighbour_y][neighbour_x] and (i != 0 and j != 0):
                    count += 1
        return count

    def mapGenerationStep(self, oldMap, deathLimit, birthLimit):
        # print(toStringMap(oldMap))
        newMap = np.zeros((len(oldMap), len(oldMap[0])))
        # for line in range(len(oldMap)):
        #   newMap[line] = [(False) for _ in range(len(oldMap[0]))]
        for y in range(len(oldMap)):
            for x in range(len(oldMap[0])):
                liveNeighbours = self.mapCountAliveNeighbours(oldMap, x, y)
                if oldMap[y][x]:
                    newMap[y][x] = liveNeighbours >= deathLimit
                else:
                    newMap[y][x] = liveNeighbours >= birthLimit
        return newMap

    def generateMap(self, width, height):
        # Game of life like algorythm is used to build map
        chanceToStartAlive = 0.65
        deathLimit = 3
        birthLimit = 4
        numberOfSteps = 3

        # generate empty map
        cellmap = np.zeros((height, width))
        #  Initialise random map with "alive" parts
        for line in range(height):
            cellmap[line] = [
                (self.np_random.random() < chanceToStartAlive) for _ in range(width)
            ]

        for _ in range(numberOfSteps):
            cellmap = self.mapGenerationStep(cellmap, deathLimit, birthLimit)
        return cellmap

    def toStringMap(self, map):
        visualMap = ""
        for y in range(len(map)):
            for x in range(len(map[0])):
                if map[y][x]:
                    visualMap += u"\u2588"
                else:
                    visualMap += " "
            visualMap += "\n"
        return visualMap
