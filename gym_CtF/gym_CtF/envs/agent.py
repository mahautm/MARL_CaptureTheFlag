class Agent:

  def __init__(self, x, y, team):
    self.posX = x
    self.posY = y
    self.team = team
    self.holdingFlag = False
    self.active = True
    self.reward = 0;
    self.visionRange = 7 # //!! This information must go in the JSON file which will hold all modifiable parametres

  def move(self,direction, map):
    # direction must be a table with 4 values, either 0 or 1. 
    # first value is left, second right, third up, fourth down

    # we check on the map if there is a wall at destination
    if(map[self.posY + direction[2] - direction[3]][self.posX + direction[0] - direction[1]] == 0.0):
      # without wall, the agent moves to destination
      map[self.posY][self.posX] = False
      self.posY += direction[2] - direction[3]
      self.posX +=direction[0] - direction[1]
      map[self.posY][self.posX] = True


  def attack(self, map, agents, flags): # !! Is it really necessary to carry around those variables just for the size I need ?
  # For now the attack mechanism has no cooldown, and seems to be something that should always be active.
  # Attack is only possible on your half of the map
    if (self.team == 1 and self.posY < len(map)/2) or (self.team == 2 and self.posY > len(map)/2):
      for agent in agents:
        # You may only attack enemies touching you, from the opposing team
        if agent.team != self.team and abs(self.posX - agent.posX) <= 1 and abs(self.posY - agent.posY) <= 1:
          # Warn of agent and death, and disactivate him
          print("Agent from team " + agent.team + " has been killed")
          agent.active = False
    
    # Attacking the enemy flag grants victory
    # //?\\ Maybe allowing your team's flag to be carried in the future would be a good add on
    for flag in flags:
      if flag.team != self.team and abs(self.posX - flag.posX) <= 1 and abs(self.posY - flag.posY) <= 1:
        print("Flag has been captured, victory to team " + self.team)
        self.reward = 1000;

  def sight(self,map,flags,agents):
    size = (self.visionRange,self.visionRange)
    visibleWalls = np.zeros(size)
    visibleFlags = np.zeros(size)
    visibleFriends = np.zeros(size)
    visibleEnemies = np.zeros(size)

    for i in range(self.visionRange):
      for j in range(self.visionRange):
        # First we check the walls that are in line of sight
        # The use of min and max ensures that if an agent is on the border of the map,
        #  it just sees the border wall being replicated, whatever the size of its vision Range
        # print(self.posY+i-1,self.posX+j-1)
        visibleWalls[i][j]=map[min(len(map)-1,max(0,self.posY+i-1))][min(len(map[0])-1,max(0,self.posX+j-1))]



        # Then we check if agents are in this zone  
        for agent in agents:
          if agent.posX == self.posX-j-1 and agent.posY==self.posY-i-1:
            visibleFriends[i][j] = (agent.team == self.team)
            visibleEnemies[i][j] = not visibleFriends[i][j]
          else:
            visibleFriends[i][j] = False
            visibleEnemies[i][j] = False

        # Finally we check if a flag is in view
        for flag in flags:
          if flag.posX == self.posX-j-1 and flag.posY==self.posY-i-1:
            visibleFlags[i][j] = True

    TotalMap = [visibleWalls,visibleFlags,visibleFriends,visibleEnemies]
    return TotalMap