import gym
import random
from gym import error, spaces, utils
from gym.utils import seeding

class CtFEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    ...
  def step(self, action):
    ...
  def reset(self):
    ...
  def render(self, mode='human'):
    ...
  def close(self):
    ...

  def mapGenerationStep(oldMap, deathLimit, birthLimit):
    newMap = [[False]*(len(oldMap[0]))]*len(oldMap)
    for x in range(len(oldMap[0])):
      for y in range(len(oldMap)):
        liveNeighbours = mapCountAliveNeighbours(oldMap,x,y)
        if oldMap[x][y]:
          newMap[x][y] = (liveNeighbours >= deathLimit)
        else:
          newMap[x][y] = (liveNeighbours <= birthLimit)
    return newMap
        

  def mapCountAliveNeighbours(map,x,y):
    count = 0;
    for i in [-1,1]:
      for j in [-1,1]:
            neighbour_x = x+i
            neighbour_y = y+j
            # In case the index we're looking off the edge of the map
            if neighbour_x < 0 or neighbour_y < 0 or neighbour_x >= len(map) or neighbour_y >= len(map[0]):
              count = count + 1
            # Otherwise, a normal check of the neighbour
            elif(map[neighbour_x][neighbour_y]):
              count = count + 1
    return count



  def generateMap(width,height):
    # Game of life like algorythm is used to build map
    chanceToStartAlive = 0.45
    deathLimit = 4
    birthLimit = 3
    numberOfSteps = 3
    # generate empty map
    cellmap = [[False]*(width)]*height

    # Initialise random map with "alive" parts
    for i in range(width):
      for j in range(height):
        if random.random() < chanceToStartAlive:
          cellmap[i][j] = True;

    for i in range (numberOfSteps):
      cellmap = mapGenerationStep(cellmap,deathLimit,birthLimit)
    return cellmap 

