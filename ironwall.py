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

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

#######################################################################
#This class hold the code for the defensive agent. At a high level,
#this agents goal is to find its way to the border between teams,
#It will then stay at the border and attack enemies that wander into
#territory
#NOTE: The getBorderCells() method was sourced from vidar.py as it was a
#much cleaner implementation than our previous getBorderCells() method.
#######################################################################
class DefensiveAgent1(CaptureAgent):

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
    redX = (layoutX - 1) / 2
    blueX = (int)(math.ceil((float)(layoutX - 1) / 2))

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

  def chooseAction(self, gameState):
    """
    Returns the best action to make as decided upon by the getBestDirection() method
    :param gameState: The variables of the current state
    :return: The best direction for the agent to move in
    """
    return self.getBestDirection(gameState)
