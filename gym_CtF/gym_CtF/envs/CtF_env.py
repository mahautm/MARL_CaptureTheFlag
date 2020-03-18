import gym
import random

from gym_CtF.envs.flag import Flag
from gym_CtF.envs.agent import Agent

import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding

class CtFEnv(gym.Env):
      """
    Description:
    A random map is generated with obstacles. 
    Two teams of agents are generated on opposite sides of the map.
    They each must capture the other team's flag without being killed by their opponent.
    First team to capture a flag wins.

    Observation: 
        Type: Box(4)
        Num	Observation                 Min         Max
        0	Cart Position             -4.8            4.8
        1	Cart Velocity             -Inf            Inf
        2	Pole Angle                 -24 deg        24 deg
        3	Pole Velocity At Tip      -Inf            Inf
        
    Actions:
        Type: Discrete(2)
        Num	Action
        0	Push cart to the left
        1	Push cart to the right
        
    Reward:
        Reward is 1 for every step taken, including the termination step
    Starting State:
        All observations are assigned a uniform random value in [-0.05..0.05]
    Episode Termination:
        Pole Angle is more than 12 degrees
        Cart Position is more than 2.4 (center of the cart reaches the edge of the display)
        Episode length is greater than 200
        Solved Requirements
        Considered solved when the average reward is greater than or equal to 195.0 over 100 consecutive trials.
    """
  
  
  
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.done = False
    self.map = self.generateMap(100,40)
    # There shall be two teams to begin with
    self.nbTeamMembers = 5
    # This is what the agents will be allowed to see each turn --> The observation space
    # self.state = spaces.Box(low=0, high=2.0, shape=(self.nbTeamMembers * 2, 4), dtype=np.int32)
    self.action_space = spaces.Box(low=0, high=2.0, shape=(self.nbTeamMembers * 2, 4), dtype=np.int32)
    self.rewards = np.zeros(self.nbTeamMembers*2)

    # There might come a time where teams are generated in a locked space
    # There will be a small probability of this happening.
    # It might later be dealt with by allowing interactions with environment
    self.agents = []
    self.flags = []

    # First team Flag is built
    self.flags.append(Flag(1,1,1))
    # A flag, unlike a wall, can share its space, we remove walls on this location
    self.map[1][1] = False

    # First team members are assigned starting position in top left corner
    for i in range(self.nbTeamMembers):
      # positioned so as to be spaced by one from each other
      self.agents.append(Agent((i+1)*2,2,1))
      # We add a Wall : You wannot walk on an agent
      self.map[2][(i+1)*2] = True

    
    #  Same for second Flag and team members, in bottom right corner
    self.flags.append(Flag(len(self.map[0])-2,len(self.map)-2,2))
    self.map[len(self.map)-2][len(self.map[0])-2] = False
    for i in range(self.nbTeamMembers):
      self.agents.append(Agent(len(self.map[0])-(i+2)*2,len(self.map)-3,2))
      self.map[len(self.map)-3][len(self.map[0])-(i+2)*2] = True

  def step(self, action) :
    # checkups for data structure
    if len(self.agents) != len(action):
      print("Invalid action : number of agents has been set to " + len(self.agents) + " but you only gave an action of size " + len(action))

    assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))

      return [self.state, self.rewards, self.done, self.add]
    else:
      self.state = []
      self.rewards = []

      for agentNb in range(len(self.agents)):
        self.agents[agentNb].move(action[agentNb][0],self.map)
        if action[agentNb][1] == 1:
          self.agents[agentNb].attackself(map,self.agents,self.flags)

        self.state.append(self.agents[agentNb].sight(self.map,self.flags, self.agents))
        # //!! Beware, here the reward is set individually. No team reward is assigned !!\\
        rew = self.agents[agentNb].reward
        self.rewards.append(rew)
        # for now rewards are only assigned on victory, no heuristics
        if rew != 0:
          self.done = True

    # returns, in order, the state, the reward, and wether the game is over
    return [self.state, self.rewards, self.done, self.add]

    # In agents there should be a table per agent, and inside that movement, then other actions

    

  def reset(self):
    # Maybe there is a difference between __init__ and this. If so I have not spotted it
    self.done = False
    self.map = self.generateMap(100,40)
    self.nbTeamMembers = 5
    self.state = np.zeros(self.nbTeamMembers*2,4)
    self.rewards = np.zeros(self.nbTeamMembers*2)
    self.agents = []
    self.flags = []

    self.flags.append(Flag(1,1,1))
    self.map[1][1] = False

    for i in range(self.nbTeamMembers):
      self.agents.append(Agent((i+1)*2,2,1))
      self.map[2][(i+1)*2] = True

    
    self.flags.append(Flag(len(self.map[0])-2,len(self.map)-2,2))
    self.map[len(self.map)-2][len(self.map[0])-2] = False
    for i in range(self.nbTeamMembers):
      self.agents.append(Agent(len(self.map[0])-(i+2)*2,len(self.map)-3,2))
      self.map[len(self.map)-3][len(self.map[0])-(i+2)*2] = True

      
  def render(self, mode='human'):
    ...


  # No idea what this one does or is supposed to do
  # def close(self):
  #   ...

  def mapCountAliveNeighbours(self,map,x,y):
    count = 0
    for i in range(3):
      for j in range(3):
            neighbour_x = x+j-1
            neighbour_y = y+i-1
            # In case the index we're looking off the edge of the map
            if (neighbour_x < 0 or neighbour_y < 0 or neighbour_y >= len(map) or neighbour_x >= len(map[0])):
              count += 1
            # Otherwise, a normal check of the neighbour
            elif(map[neighbour_y][neighbour_x] and (i != 0 and j !=0)):
              count += 1
    return count

  def mapGenerationStep(self, oldMap, deathLimit, birthLimit):
    # print(toStringMap(oldMap))
    newMap = np.zeros((len(oldMap),len(oldMap[0])))
    # for line in range(len(oldMap)):
    #   newMap[line] = [(False) for _ in range(len(oldMap[0]))]
    for y in range(len(oldMap)):
      for x in range(len(oldMap[0])):
        liveNeighbours = self.mapCountAliveNeighbours(oldMap,x,y)
        if oldMap[y][x]:
          newMap[y][x] = (liveNeighbours >= deathLimit)
        else:
          newMap[y][x] = (liveNeighbours >= birthLimit)
    return newMap



  def generateMap(self, width,height):
    # Game of life like algorythm is used to build map
    chanceToStartAlive = 0.65
    deathLimit = 3
    birthLimit = 4
    numberOfSteps = 3
  
    # generate empty map
    cellmap = np.zeros((height, width))
    #  Initialise random map with "alive" parts
    for line in range(height):
      cellmap[line] = [(random.random()<chanceToStartAlive) for _ in range(width)]

    for i in range (numberOfSteps):
      cellmap = self.mapGenerationStep(cellmap,deathLimit,birthLimit)
    return cellmap 

  def toStringMap(self,map):
    visualMap = ''
    for y in range(len(map)):
      for x in range(len(map[0])):
        if map[y][x]:
          visualMap+=u"\u2588"
        else:
          visualMap+=" "
      visualMap+='\n'
    return(visualMap)
