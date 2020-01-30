# baselineTeam.py
# ---------------
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

# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from __future__ import print_function
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint
from game import Actions
#TODO:Check for uneeded imports.

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'agent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

###################################################
# Base class for an offensive bot. Sets up initial state,
# and also chooses the maximizing action. I originally
# wanted to have all the code contained in OffensiveReflexAgent,
# and inherit CaptureAgent, however weird behavior started 
# to occur and I did not have enough time to investigate
# the problem further. Im not sure if it was the removal
# of any of these functions included here.
# (In particular the original getFeatures and getWeights methods).
###################################################
class agent(CaptureAgent):
    def chooseAction(self, gameState):
        return random.choice(gameState.getLegalActions(self.index))

class OffensiveReflexAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    """
    Function to establish initial states of the game.
    This is where its goal is to find food or go straight 
    for the power capsule.
    :param gameState: The variables of the current state.
    """
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.goal = self.rushCapsule(gameState)
    self.walls = gameState.getWalls()
    self.costFn = lambda x: 1
    self.actionList = self.breadthFirstSearch(gameState)
    print(self.actionList)

  def rushCapsule(self, gameState):
    """
    This method is to decide what strategy the offensive bot will first
    try to do. It has a 33% chance of going immediately to the power capsule,
    which is a 'cheese' strat. The other chance it will seek to find the
    closest food.
    :param gameState: The variables of the current state.
    """
    rand = random.randint(1, 4)
    if rand == 3:
      return self.getCapsules(gameState)
    else:
        # These values are hardcoded, seem to be least conflict area
        # travels along the outer edge of the map first.
        if gameState.isOnRedTeam(self.index):
            return (21, 1)
        else:
            return (10, 14)

  def getClosestFood(self, gameState):
    """
    Function that returns the (x, y) coordinate of the closest food near
    an agent. This behavior isnt too advanced as it does not account for 
    enemies in the way to the food.
    """
    foodList = self.getFood(gameState).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = gameState.getAgentState(self.index).getPosition()
      min_pos = 9999
      best_choice = None
      for food in foodList:
        temp_pos = self.getMazeDistance(myPos, food)
        temp_food = food
        if temp_pos < min_pos:
          min_pos = temp_pos
          best_choice = food
    return best_choice

  def isGoalState(self, state):
    """
    Returns a boolean that checks to see whether or not current (x, y)
    matches goal (x, y).
    :param state: Current (x, y) that is being checked.
    :param gameState: The variables of the current state.
    """
    isGoal = state == self.goal
    return isGoal

  def updateGoalState(self, goal):
    """
    Changes the (x, y) destination to a new goal.
    :param goal: New (x, y) coordinate that represents end target.
    """
    self.debugClear()
    self.goal = goal

  def checkGoalState(self):
   """
   Check for enemies on or near the goal, (x, y).
   """
   print(self.index)
   print('goal', self.goal)
   raw_input()
   goalDist = self.getMazeDistance(self.index, self.goal)
   if goalDist < 5:
     print('check')

  def breadthFirstSearch(self, gameState):
    current_pos = gameState.getAgentPosition(self.index)

    if self.isGoalState(current_pos):
      return []
    myQueue = util.Queue()
    visitedNodes = []

    myQueue.push((current_pos, []))
    while not myQueue.isEmpty():
      current_pos, actions = myQueue.pop()
      if current_pos not in visitedNodes:
        visitedNodes.append(current_pos)
      if self.isGoalState(current_pos):
        #print(actions)
        return actions

      for nextNode, action, cost in self.getSuccessors(current_pos):
        newAction = actions + [action]
        myQueue.push((nextNode, newAction))

  def hasDied(self, gameState):
    if len(self.observationHistory) > 10:
       obsHistory = self.observationHistory[len(self.observationHistory)-2]
       posHistory = obsHistory.getAgentPosition(self.index)
       currentPos = gameState.getAgentPosition(self.index)
       distHistory = self.getMazeDistance(currentPos, posHistory)
       if distHistory > 1:
         return True
    return False

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    #raw_input()
    #self.checkGoalState()

    if self.hasDied(gameState):
      self.actionList = []
      self.updateGoalState(self.getClosestFood(gameState))

    self.debugDraw(self.goal, (1, 0, 0))
    #raw_input()
    if len(self.actionList) == 0:
      self.updateGoalState(self.getClosestFood(gameState))
      self.actionList = self.breadthFirstSearch(gameState)

    print(self.actionList)
    return self.actionList.pop(0)
    #actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    #values = [self.evaluate(gameState, a) for a in actions]
    #if self.index == 1:
      #print(values, file=sys.stderr)
      # print(self.getPreviousObservation(), file=sys.stderr)

    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    #maxValue = max(values)
    #bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    # if self.index == 1:
    #   print(bestActions, file=sys.stderr)

    #foodLeft = len(self.getFood(gameState).asList())

    #if foodLeft <= 2 or gameState.getAgentState(self.index).numCarrying >= 3:
      #bestDist = 9999
      #for action in actions:
        #successor = self.getSuccessor(gameState, action)
        #pos2 = successor.getAgentPosition(self.index)
	#dist = self.getMazeDistance(self.start,pos2)
        #if dist < bestDist:
          #bestAction = action
          #bestDist = dist
      #return bestAction

    #return random.choice(bestActions)

  def getSuccessors(self, state):
    successors = []
    bestDist = 9999
    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state
      dx, dy = Actions.directionToVector(action)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        nextState = (nextx, nexty)
        cost = self.costFn(nextState)

        dist = self.getMazeDistance(nextState, self.goal)
        if dist < bestDist:
          bestDist = dist
          bestAction = action
          bestState = nextState
    successors.append( (bestState, bestAction, cost) )
    return successors

  def getBorderCells(self, gameState):
    """
    Returns a list of cells that represent the border between teams
    :param gameState: The variables of the current state
    :return: List of cells that is on our teams side, but borders the other team
    Important Note: This code was sourced from vidar.py. As mentioned above, it was
    a much cleaner implementation than our previous getBorderCells method which inolved
    heavy list manipulations and many loops
    """

    # List that will hold the cells that lie on our teams side, but border the other team
    borderCells = []

    # Obtain the matrix of walls around the entire map
    wallsMatrix = gameState.data.layout.walls
    wallsList = wallsMatrix.asList()

    # Using the width of the map, calculate the Red and Blue teams border cell column value
    # The calculations return 15.5, the red teams side ends at 15, blue teams side starts at 16, hence ceil()
    layoutX = wallsMatrix.width
    redX = (layoutX - 1) / 2
    blueX = (int)(math.ceil((float)(layoutX - 1) / 2))

    # Using the height of the map, the number of rows, loop through the number of rows
    # and add the cells to the return list that are not walls
    layoutY = wallsMatrix.height - 1
    if (gameState.isOnRedTeam(self.index)):
      for y in range(1, layoutY - 1):
        if ((redX, y) not in wallsList):
          borderCells.append((redX, y))
    else:
      for y in range(1, layoutY - 1):
        if ((blueX, y) not in wallsList):
          borderCells.append((blueX, y))

    return borderCells

