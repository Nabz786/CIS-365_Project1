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

class ReflexCaptureAgent(CaptureAgent):

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
            #return self.getClosestFood(gameState)
            #return (21, 1)
            #return (3, 5)
            return (3, 10)
            #return (17, 6)
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

  def checkGoalState(self, goal):
   """
   Check for enemies near the goal, (x, y).
   """
   pass

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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)

    if self.index == 1:
      print(str(features) + str(weights), file=sys.stderr)
      # print(gameState.getAgentState(self.index)) # Print out a text representation of the world.

    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

###################################################
# This class defines an offensive agent. The defined
# behavior of this agent is to prioritize a goal,
# which is a certain (x, y) coordinate. It then creates a list
# of actions to take to reach its gaol based on a
# breadthFirstSearch algorithm.
# Improvements need to be made with enemy interaction. 
##################################################
class OffensiveReflexAgent(ReflexCaptureAgent):

  def getFeatures(self, gameState, action):
    """
    Function that creates a list of game features to change values of the 
    available moves to make.
    :param gameState: The variables of the current state.
    :param action: The direction of the agents move.
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      #print(successor.getAgentState(self.index))
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance


    #if self.isGoalState(myPos):
        #self.updateGoalState(self.getClosestFood(gameState))

    #print here
    #self.breadthFirstSearch(gameState)
    #string = raw_input()

    # Determine if the enemy is closer to you than they were last time
    # and you are in their territory.
    # Note: This behavior isn't perfect, and can force Pacman to cower 
    # in a corner.  I leave it up to you to improve this behavior.
    close_dist = 9999.0
    if self.index == 1 and gameState.getAgentState(self.index).isPacman:
      opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      chasers = [p for p in opp_fut_state if p.getPosition() != None and not p.isPacman]
      if len(chasers) > 0:
        close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])

      # View the action and close distance information for each 
      # possible move choice.
      # print("Action: "+str(action))
      # print("\t\t"+str(close_dist), sys.stderr)
    features['fleeEnemy'] = 1.0/close_dist
    return features

  def getWeights(self, gameState, action):
    """
    Function that returns the weights of each associated parameter.
    :param gameState: The variables of the current state.
    :param action: The direction of the agents move.
    """
    return {'successorScore': 100, 'distanceToFood': -1.5, 'fleeEnemy': -100.0}

