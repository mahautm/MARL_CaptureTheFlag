import gym
import random
from flag import Flag
from agent import Agent
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding

class CtFEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.map = generateMap(100,40)
    # There shall be two teams to begin with
    self.nbTeamMembers = 5
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

  def step(self, action):
    ...
  def reset(self):
    ...
  def render(self, mode='human'):
    ...
  def close(self):
    ...

  def mapGenerationStep(oldMap, deathLimit, birthLimit):
    # print(toStringMap(oldMap))
    newMap = np.zeros((len(oldMap),len(oldMap[0])))
    # for line in range(len(oldMap)):
    #   newMap[line] = [(False) for _ in range(len(oldMap[0]))]
    for y in range(len(oldMap)):
      for x in range(len(oldMap[0])):
        liveNeighbours = mapCountAliveNeighbours(oldMap,x,y)
        if oldMap[y][x]:
          newMap[y][x] = (liveNeighbours >= deathLimit)
        else:
          newMap[y][x] = (liveNeighbours >= birthLimit)
    return newMap
        

  def mapCountAliveNeighbours(map,x,y):
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



  def generateMap(width,height):
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
      cellmap = mapGenerationStep(cellmap,deathLimit,birthLimit)
    return cellmap 

  def toStringMap(map):
    visualMap = ''
    for y in range(len(map)):
      for x in range(len(map[0])):
        if map[y][x]:
          visualMap+=u"\u2588"
        else:
          visualMap+=" "
      visualMap+='\n'
    return(visualMap)