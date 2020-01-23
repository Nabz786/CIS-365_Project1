# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util, math
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveAgent1', second = 'DefensiveAgent2'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class BaseAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index);
    CaptureAgent.registerInitialState(self, gameState);

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor


  def checkValidDirection(self, index, legalActions, wall2):

    bestDistance = 9999
    for a in legalActions:
      successor = self.getSuccessor(gamestate, action)
      successorPos = successor.getAgentPosition(self.index)
      distSuccessor = self.getMazeDistance(successorPos, wall2)

      if distSuccessor < bestDistance:
        bestDistance = distSuccessor
        bestAction = bestAction

      previousAction = self.observationHistory[-1].getAgentState(self.index).getDirection()
      if bestAction == previousAction:
        continue
      else: return True

  def getDirToPosition(self, agentWho, gamestate):

    #Get The legal Moves
    legalActions = gamestate.getLegalActions(self.index)

    #Get the wall boundaries
    wallCells = self.getRetreatCells(gamestate)

    #Get a random border cell and that will be our target
    targetCell = random.choice(wallCells)

    bestAction = "Stop"

    bestDistance = 9999
    for action in legalActions:
      successor = self.getSuccessor(gamestate, action)
      successorPos = successor.getAgentPosition(self.index)
      distSuccessor = self.getMazeDistance(successorPos, targetCell)

      team = self.getTeam(gamestate)
      teamDist = 0
      for t in team:
        if self.index == t:
          continue
        else:
          teamPos = gamestate.getAgentPosition(t)
          teamDist = self.getMazeDistance(gamestate.getAgentPosition(self.index), teamPos)


      enemies = self.getOpponents(gamestate)
      for enemy in enemies:
        enemyPos = gamestate.getAgentPosition(enemy)
        if enemyPos != None:
          enemyDist = self.getMazeDistance(gamestate.getAgentPosition(self.index), enemyPos)
          if enemyDist <= 7 and gamestate.getAgentState(enemy).isPacman:
            bestDist = 999
            for action in legalActions:
              successor = self.getSuccessor(gamestate, action)
              successorPos = successor.getAgentPosition(self.index)
              distSuccessor = self.getMazeDistance(successorPos, enemyPos)
              if distSuccessor < bestDistance:
                bestDistance = distSuccessor
                bestAction = action
            return bestAction

      if self.getScore(gamestate) < 5:
        print('here')
        foodTarget = self.getBestDirectionOfFood(gamestate)
        if agentWho == "DefensiveAgent1":
          bestDistance = 999
          for action in legalActions:
            successor = self.getSuccessor(gamestate, action)
            successorPos = successor.getAgentPosition(self.index)
            distSuccessor = self.getMazeDistance(successorPos, foodTarget)
            if distSuccessor < bestDistance:
              bestDistance = distSuccessor
              bestAction = action
          return bestAction





      if teamDist <= 2 and len(self.observationHistory) > 25:
        rev = Directions.REVERSE[gamestate.getAgentState(self.index).configuration.direction]
        if agentWho == "DefensiveAgent2":
          return rev

      if distSuccessor < bestDistance:
        bestDistance = distSuccessor
        bestAction = action
    return bestAction


  def getRetreatCells(self, gameState):
    homeSquares = []
    wallsMatrix = gameState.data.layout.walls
    wallsList = wallsMatrix.asList()
    layoutX = wallsMatrix.width
    redX = (layoutX - 1) / 2
    blueX = (int)(math.ceil((float)(layoutX - 1) / 2))

    layoutY = wallsMatrix.height - 1

    if (gameState.isOnRedTeam(self.index)):
      for y in range(1, layoutY - 1):
        if ((redX, y) not in wallsList):
          homeSquares.append((redX, y))
    else:
      for y in range(1, layoutY - 1):
        if ((blueX, y) not in wallsList):
          homeSquares.append((blueX, y))

    return homeSquares

  def getBestDirectionOfFood(self, gameState):

    #Get the agents current position
    currentLocation = gameState.getAgentPosition(self.index)

    #Get the current list of food
    foodList = self.getFood(gameState).asList()

    #Find the food that's the smallest distance away
    minDist = 1000000
    minDistIter = 0
    nearestFoodIndex = 0

    for food in foodList:
      distanceToFood = self.getMazeDistance(currentLocation, food)
      if distanceToFood < minDist:
        minDist = distanceToFood
        nearestFoodIndex = minDistIter
      minDistIter+=1

    foodToPass = foodList[nearestFoodIndex]
    return foodToPass



class DefensiveAgent1(BaseAgent):



  def chooseAction(self, gameState):



    #If the amount of food left on the board is greater than 2, go find it
    return self.getDirToPosition("agent1", gameState)
    '''
    You should change this in your own agent.
    '''

    #return random.choice(actions)


class DefensiveAgent2(BaseAgent):

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    return self.getDirToPosition("agent2", gameState)
    #actions = gameState.getLegalActions(self.index)
    '''
    You should change this in your own agent.
    '''

    #return random.choice(actions)







class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

