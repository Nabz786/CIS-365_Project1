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

# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from __future__ import print_function
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys, math
from game import Directions
import game
from util import nearestPoint
from game import Actions

def createTeam(firstIndex, secondIndex, isRed,
        first = 'OffensiveAgent', second = 'DefensiveAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

#######################################################################
#Offensive Agent class that inherits functions from the capture agent.
#This agent uses the breadth first search (BFS) for shortest path finding.
#Through a regular game cycle, the offensive agent algorithm will build
#a list of actions that represent a path to a algorithmically calculated goal
#The following are possible goals:
#Closest Food or Closest Location on ones friendly map area
#
#By traversing the shortest path calculated by the BFS algorithm, the
#Agent will leverage additional logic to attempt to dodge enemies,
#as well as determine how much food to collect
#######################################################################
class OffensiveAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    """
    Function to establish initial states of the game.
    This is where the offensive agent gets its first target destination (self.goal).
    Which is a point that avoids the agent traveling through the middle of the map at first.
    :param gameState: The variables of the current state.
    """
    CaptureAgent.registerInitialState(self, gameState)
    self.goal = self.defineFirstGoal(gameState)
    self.walls = gameState.getWalls()
    self.actionList = self.breadthFirstSearch(gameState)

  def defineFirstGoal(self, gameState):
    """
    Influnces the strategy the offensive bot will first try to do.
    The first goal is hardcoded because it points the agent to the area
    of least conflict making sure that the agent travels along the outer edge of the map.
    :param gameState: The variables of the current state.
    """

    #The tuples below represent points along the bottom and top walls
    if gameState.isOnRedTeam(self.index):
      return (21, 1)
    else:
      return (10, 14)

  def getClosestFood(self, gameState):
    """
    Returns the (x, y) coordinate of the closest food to an agent
    :param gameState: The variables of the current state
    :returns best_choice: The closest food to the agent
    """

    #Get the current list of food and our agents position
    foodList = self.getFood(gameState).asList()
    currentAgentPosition = gameState.getAgentPosition(self.index)

    #Create temporary variables to keep track of state in the loop below
    bestFood = (16, 2)
    bestDist = 9999

    #Loop through the list of food, find the closest food, return the position tuple
    if len(foodList) > 0:
      for food in foodList:
        distanceToFood = self.getMazeDistance(currentAgentPosition, food)

        if distanceToFood < bestDist:
          bestDist = distanceToFood
          bestFood = food
    return bestFood

  def isGoalState(self, state):
    """
    Returns a boolean that indicates whether or not current position (x, y)
    matches goal position (x,y)
    :param state: Current (x, y) that is being checked.
    :param gameState: The variables of the current state.
    """
    isGoal = state == self.goal
    return isGoal

  def updateGoalState(self, goal, gamestate):
    """
    Changes the (x, y) goal position to a new goal position. This method will
    assist in determining where our agent will proceed to after its reached its target
    :param goal: New (x, y) coordinate that represents end target.
    """

    howMuchFoodToEat = 1

    #Check to see if the capsule has been eaten and the enemies are currently scared
    #If this is true, our agent will get 6 pieces of food before returning, if not,
    #It will only collect one piece
    if len(self.getCapsules(gamestate)) == 0:
      enemies = self.getOpponents(gamestate)
      if gamestate.getAgentState(enemies[0]).scaredTimer == 0:
        howMuchFoodToEat = 1
      else:
        howMuchFoodToEat = 6

    numCarrying = gamestate.getAgentState(self.index).numCarrying

    #Check to see if the agent is carrying the target amount, if so, find the closest
    #"home" cell and update our target. If not, continue to the current goal
    if numCarrying >= howMuchFoodToEat:
      borderCells = self.getBorderCells(gamestate)
      bestDist = 9999
      bestCell = borderCells[0]
      currentPos = gamestate.getAgentPosition(self.index)
      for cell in borderCells:
        dist = self.getMazeDistance(currentPos, cell)
        if dist < bestDist:
          bestDist = dist
          bestCell = cell
      self.goal = bestCell
      return
    else:
      self.goal = goal

  def breadthFirstSearch(self, gameState):
    """
    Search algorithm that finds a path to the current goal (x,y) position.
    This is called everytime the goal is updated, to build the shortest path to the target.
    :param gameState: The variables of the current state.
    :returns actions: List of actions (N,S,E,W), that corresponds from index
    of agent to end target
    """

    current_pos = gameState.getAgentPosition(self.index)

    #Return an empty list if we have reached the specified goal
    if self.isGoalState(current_pos):
      return []

    myQueue = util.Queue()
    visitedNodes = []

    myQueue.push((current_pos, []))
    while not myQueue.isEmpty():
      current_pos, actions = myQueue.pop()
      if current_pos not in visitedNodes:
        #adds to list of visited locations
        visitedNodes.append(current_pos)
      if self.isGoalState(current_pos):
        return actions

      #This takes all of the next possible moves for the current position
      #and pushes it to the queue
      for nextNode, action in self.getSuccessors(current_pos):
        newAction = actions + [action]
        #Next node is the successor new (x, y) and newAction is that action
        #that it takes to get there
        myQueue.push((nextNode, newAction))

  def hasDied(self, gameState):
    """
    Function that checks if the offensive bot has been eaten, by checking the previous observation
    :param gameState: The variables of the current state.
    :return boolean: True or false, depending on if eaten or not
    """

    #We only want to check the observation history if a decent history exists
    if len(self.observationHistory) > 10:

       #Obtain the last state and from it obtain the agents last position (posHistory)
       obsHistory = self.observationHistory[len(self.observationHistory)-2]
       posHistory = obsHistory.getAgentPosition(self.index)

       #Compare the agents current position to its last, if the distance is > 1 we teleported (respawned after dying)
       currentPos = gameState.getAgentPosition(self.index)
       distHistory = self.getMazeDistance(currentPos, posHistory)
       if distHistory > 1:
         return True
    return False

  def chooseAction(self, gameState):
    """
    This is essentially the "Main" method of the agent, it decides where the agent will go
    Every iteration on this method will pop and return the action in the actionList returned by the BFS
    Goals are also updated if necessary
    :param gameState: The variables of the current state.
    """

    #Check if our agent has died, if so create a new actionList, and update the goal
    if self.hasDied(gameState):
      self.actionList = []
      self.updateGoalState(self.getClosestFood(gameState), gameState)

    enemies = self.getOpponents(gameState)

    #This block checks for enemies within 6 map spaces of our agent, if one is found
    #It will find the closest friendly space to the agent, update the goal, and find the BFS path to the goal
    for enemy in enemies:
      enemyPosition = gameState.getAgentPosition(enemy)
      if enemyPosition != None:
        enemyDist = self.getMazeDistance(gameState.getAgentPosition(self.index), enemyPosition)

        #If the enemy is within 6 spaces and our agent is pacman and the enemy is a ghost
        #We are in enemy territory and are being chased
        if enemyDist <= 6 and (gameState.getAgentState(self.index).isPacman and
                               not gameState.getAgentState(enemy).isPacman):

            #Obtain the cells that border the enemy territory and find the closest one
            borderCells = self.getBorderCells(gameState)
            bestDist = 9999
            bestCell = borderCells[0]
            currentPos = gameState.getAgentPosition(self.index)
            for cell in borderCells:
              dist = self.getMazeDistance(currentPos, cell)
              if dist < bestDist:
                bestDist = dist
                bestCell = cell
            #Update the goal with the closest friendly cell
            self.goal = bestCell
            self.actionList = []
            #Find the actions that will take us to the cell
            self.actionList = self.breadthFirstSearch(gameState)

    #By Default, if the action list is empty, find the nearest food to the agent,
    #Update the goal with the food location and repopulate the action list with the BFS path to the food
    if len(self.actionList) == 0:
      self.updateGoalState(self.getClosestFood(gameState), gameState)
      self.actionList = []
      self.actionList = self.breadthFirstSearch(gameState)

    return self.actionList.pop(0)

  def getSuccessors(self, state):
    """
    This method is called by the search function to check if a 
    state has additional moves it can make.
    :param state: the (x, y) coordinate of a position.
    :return successors: Tuple that hold the best action to make and resulting map position

    Important Note: This method was taken from searchAgent.py, as it was used
    during the initial implementation of BFS in search.py to permutate
    the next possible moves
    """
    successors = []
    bestDist = 9999
    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state

      #converts direction to a coordinate
      #Ex: Directions.North = (1, 0)
      dx, dy = Actions.directionToVector(action)

      #apply new coordinate
      nextx, nexty = int(x + dx), int(y + dy)

      #check if its a legal move
      if not self.walls[nextx][nexty]:
        nextState = (nextx, nexty)
        dist = self.getMazeDistance(nextState, self.goal)

        if dist < bestDist:
          bestDist = dist
          bestAction = action
          bestState = nextState
    successors.append((bestState, bestAction))
    return successors

  def getBorderCells(self, gameState):
    """
    Returns a list of cells that represent the border between teams
    :param gameState: The variables of the current state
    :return: List of cells that is on our teams side, but borders the other team
    Important Note: This code was sourced from vidar.py. As mentioned above, it was
    a much cleaner implementation than our previous getBorderCells method. It has also
    been modified to return a different column of border cells
    """

    # List that will hold the cells that lie on our teams side, but border the other team
    borderCells = []

    # Obtain the matrix of walls around the entire map
    wallsMatrix = gameState.data.layout.walls
    wallsList = wallsMatrix.asList()

    # Using the width of the map, calculate the Red and Blue teams border cell column value
    #Offset the final values by 3 to bring our agents further into friendly territory
    layoutX = wallsMatrix.width
    redX = ((layoutX - 1) / 2) - 3
    blueX = ((int)((math.ceil((float)(layoutX - 1) / 2)))) + 3

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

#######################################################################
#Defensive agent class that leverages the cells along the border to
#create a patrolling movement by default. If the agent detects an
#enemy it will find the path to the enemy agent greedily.
#######################################################################
class DefensiveAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    """
    Registers the 1st state when the game starts with the system
    :param gameState: The variables of the current state
    """
    self.start = gameState.getAgentPosition(self.index);
    CaptureAgent.registerInitialState(self, gameState);

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    :param gameState:
    :param action: The move the successor will make (N,S,E,W)
    :returns successor: A new agent with the action specified applied on it
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def getBestDirection(self, gamestate):
    """
    Returns a direction for the agent to move in, the direction
    is calculated through specific checks highlighed below
    :param gamestate: The variables of the current state
    :return: bestAction: The best direction for the bot to move in
    """

    # Get The legal moves and obtain a list of cells a long the border between teams
    legalActions = gamestate.getLegalActions(self.index)
    borderCell = self.getBorderCells(gamestate)

    # From the borderCell list, choose a random cell to be our target
    targetCell = random.choice(borderCell)

    #By default, have the agent stop if there isn't a valid move. Set a placeholder distance value
    bestAction = "Stop"
    bestDistance = 9999

    for action in legalActions:
      enemies = self.getOpponents(gamestate)

      #Loop through the list of enemy positions and check if we can see an enemy (enemyPostion != None)
      #If we see an enemy, compare the agent and the enemy's distance
      #If the enemy is within 10 distance units of the agent and is on our side (enemy.isPacman == true)
      #Pursue it, by finding the action that gets us closest, return that action
      for enemy in enemies:
        enemyPosition = gamestate.getAgentPosition(enemy)
        if enemyPosition != None:
          enemyDist = self.getMazeDistance(gamestate.getAgentPosition(self.index), enemyPosition)
          if enemyDist <= 10 and gamestate.getAgentState(enemy).isPacman:
            for action in legalActions:
              successor = self.getSuccessor(gamestate, action)
              successorPos = successor.getAgentPosition(self.index)
              distSuccessor = self.getMazeDistance(successorPos, enemyPosition)
              if distSuccessor < bestDistance:
                bestDistance = distSuccessor
                bestAction = action
            return bestAction

      #This code will be executed if an enemy wasn't detected
      #We return the action of the successor agent that is closest to the target wall after looping through all actions.
      successor = self.getSuccessor(gamestate, action)
      successorPos = successor.getAgentPosition(self.index)
      distSuccessor = self.getMazeDistance(successorPos, targetCell)

      if distSuccessor < bestDistance:
        bestDistance = distSuccessor
        bestAction = action
    return bestAction

  def getBorderCells(self, gameState):
    """
    Returns a list of cells that represent the border between teams
    :param gameState: The variables of the current state
    :return: List of cells that is on our teams side, but borders the other team
    Important Note: This code was sourced from vidar.py. As mentioned above, it was
    a much cleaner implementation than our previous getBorderCells method which inolved
    heavy list manipulations and many loops
    """

    #List that will hold the cells that lie on our teams side, but border the other team
    borderCells = []

    #Obtain the matrix of walls around the entire map
    wallsMatrix = gameState.data.layout.walls
    wallsList = wallsMatrix.asList()

    #Using the width of the map, calculate the Red and Blue teams border cell column value
    #The calculations return 15.5, the red teams side ends at 15, blue teams side starts at 16, hence ceil()
    layoutX = wallsMatrix.width
    redX = ((layoutX - 1) / 2) - 1
    blueX = ((int)((math.ceil((float)(layoutX - 1) / 2)))) + 1

    #Using the height of the map, the number of rows, loop through the number of rows
    #and add the cells to the return list that are not walls
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

  def chooseAction(self, gameState):
    """
    Returns the best action to make as decided upon by the getBestDirection() method
    :param gameState: The variables of the current state
    :return: The best direction for the agent to move in
    """
    return self.getBestDirection(gameState)


class DefensiveAgent2(CaptureAgent):

  def registerInitialState(self, gameState):
    """
    Registers the 1st state when the game starts with the system
    :param gameState: The variables of the current state
    """
    self.start = gameState.getAgentPosition(self.index);
    CaptureAgent.registerInitialState(self, gameState);

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    :param gameState:
    :param action: The move the successor will make (N,S,E,W)
    :returns successor: A new agent with the action specified applied on it
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def getBestDirection(self, gamestate):
    """
    Returns a direction for the agent to move in, the direction
    is calculated through specific checks highlighed below
    :param gamestate: The variables of the current state
    :return: bestAction: The best direction for the bot to move in
    """

    # Get The legal moves and obtain a list of cells a long the border between teams
    legalActions = gamestate.getLegalActions(self.index)
    borderCell = self.getBorderCells(gamestate)

    # From the borderCell list, choose a random cell to be our target
    targetCell = random.choice(borderCell)

    # By default, have the agent stop if there isn't a valid move. Set a placeholder distance value
    bestAction = "Stop"
    bestDistance = 9999

    for action in legalActions:
      enemies = self.getOpponents(gamestate)

      # Loop through the list of enemy positions and check if we can see an enemy (enemyPostion != None)
      # If we see an enemy, compare the agent and the enemy's distance
      # If the enemy is within 10 distance units of the agent and is on our side (enemy.isPacman == true)
      # Pursue it, by finding the action that gets us closest, return that action
      for enemy in enemies:
        enemyPosition = gamestate.getAgentPosition(enemy)
        if enemyPosition != None:
          enemyDist = self.getMazeDistance(gamestate.getAgentPosition(self.index), enemyPosition)
          if enemyDist <= 10 and gamestate.getAgentState(enemy).isPacman:
            for action in legalActions:
              successor = self.getSuccessor(gamestate, action)
              successorPos = successor.getAgentPosition(self.index)
              distSuccessor = self.getMazeDistance(successorPos, enemyPosition)
              if distSuccessor < bestDistance:
                bestDistance = distSuccessor
                bestAction = action
            return bestAction

      # This code will be executed if an enemy wasn't detected
      # We return the action of the successor agent that is closest to the target wall after looping through all actions.
      successor = self.getSuccessor(gamestate, action)
      successorPos = successor.getAgentPosition(self.index)
      distSuccessor = self.getMazeDistance(successorPos, targetCell)

      if distSuccessor < bestDistance:
        bestDistance = distSuccessor
        bestAction = action
    return bestAction

  def getBorderCells(self, gameState):
    """
    Returns a list of cells that represent the border between teams
    :param gameState: The variables of the current state
    :return: List of cells that is on our teams side, but borders the other team
    Important Note: This code was sourced from vidar.py. As mentioned above, it was
    a much cleaner implementation than our previous getBorderCells method which involved
    heavy list manipulations and many loops
    """

    # List that will hold the cells that lie on our teams side, but border the other team
    borderCells = []

    # Obtain the matrix of walls around the entire map
    wallsMatrix = gameState.data.layout.walls
    wallsList = wallsMatrix.asList()

    # Using the width of the map, calculate the Red and Blue teams border cell column value
    # Offset the final values by 1 to ensure our agent stays in friendly territory
    layoutX = wallsMatrix.width
    redX = ((layoutX - 1) / 2) - 1
    blueX = ((int)(math.ceil((float)(layoutX - 1) / 2))) + 1

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

  def chooseAction(self, gameState):
    """
    Returns the best action to make as decided upon by the getBestDirection() method
    :param gameState: The variables of the current state
    :return: The best direction for the agent to move in
    """
    return self.getBestDirection(gameState)
