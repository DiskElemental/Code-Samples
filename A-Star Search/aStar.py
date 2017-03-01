# Name: aStar.py
# Programmer: Joshua Brinkman
# Date: 2/17/2016
# Requires: node.py, Queue.py

from node import *
import Queue

# A simple implementation of the aStar searching, using the properties of the node
# Whenever a new node is generated, the Manhatten distance to the goal is
# calculated. The total pathcost to reach the node is added, and this value is
# used to determine which node to expand next.
#
# Pre: startingNodes - a list containing the stating nodes in the lower half
#                      and a list of the nding nodes on the upper half
#      gridSpace - the grid which the puzzle has been read into
#      length - the size of the grid
#      numcolors - the number of start/end pairs
#
# Post: solutionStack - returns a list of the actions taken
#       gridSpace - the paths have been written to the grid

def aStar(startingNodes, gridSpace, length, numcolors):
    endingNodes = startingNodes[numcolors:]
    tempStorage = startingNodes[:numcolors]
    initFrontier = []
    frontier = Queue.PriorityQueue(maxsize=0)
    solutionStack = []
    explored = []

    for index1 in tempStorage:
        for index2 in endingNodes:
            if(index1.contents == index2.contents):
                index1.set_goal(index2)
                index1.set_heuristic(index2)
                initFrontier.append(index1)
    initFrontier.sort()

    while True:
        if(frontier.empty() and len(initFrontier) != 0):
            frontier.put_nowait(initFrontier.pop(0))
        if(frontier.empty() and len(initFrontier) == 0):
            solutionStack.reverse()
            return solutionStack
        currentNode = frontier.get_nowait()

        if( (-1 < currentNode.xcoord -1 < length) & (currentNode.ycoord < length)):
            if(gridSpace[currentNode.xcoord-1][currentNode.ycoord] == 'e' or gridSpace[currentNode.xcoord-1][currentNode.ycoord] == currentNode.contents):
                newNode = makeNode(currentNode, 3, gridSpace)
                if(newNode not in explored):
                    frontier.put_nowait(newNode)
                    explored.append(newNode)

        if( (currentNode.xcoord < length) & ( -1 < currentNode.ycoord - 1 < length)):
            if(gridSpace[currentNode.xcoord][currentNode.ycoord - 1] == 'e' or gridSpace[currentNode.xcoord][currentNode.ycoord-1] == currentNode.contents):
                newNode = makeNode(currentNode, 2, gridSpace)
                if(newNode not in explored):
                    frontier.put_nowait(newNode)
                    explored.append(newNode)

        if( (currentNode.xcoord + 1 < length) & (currentNode.ycoord < length)):
            if(gridSpace[currentNode.xcoord + 1][currentNode.ycoord] == 'e' or gridSpace[currentNode.xcoord+1][currentNode.ycoord] == currentNode.contents):
                newNode = makeNode(currentNode, 1, gridSpace)
                if(newNode not in explored):
                    frontier.put_nowait(newNode)
                    explored.append(newNode)

        if( (currentNode.xcoord < length) & (currentNode.ycoord + 1 < length)):
            if(gridSpace[currentNode.xcoord][currentNode.ycoord+1] == 'e' or gridSpace[currentNode.xcoord][currentNode.ycoord+1] == currentNode.contents ):
                newNode = makeNode(currentNode, 0, gridSpace)
                if(newNode not in explored):
                    frontier.put_nowait(newNode)
                    explored.append(newNode)

        if(currentNode == currentNode.goalNode):
            frontier = Queue.PriorityQueue(maxsize=0)
            pathtoGoal = []
            explored = []
            while(currentNode.parentNode != None):
                solutionStack.append((currentNode.contents, currentNode.ID))
                pathtoGoal.append(currentNode)
                currentNode = currentNode.parentNode
            for index in pathtoGoal:
                gridSpace[index.xcoord][index.ycoord] = index.contents


# Wrapper function used to run the aStar functions for multiple start/end points
# Starts by creating the initial nodes, using information gained from the read-in
# Then runs aStar passing it the list of starting points
#
# Pre:  length - size of the grid
#       numColors - the number of colors
#       gridSpace - the grid which the puzzle has been read into
#       foundSymbols - list containing the coordinates of the starting positions
#
# Post: gridSpace - has had the paths written to it
#       solutionStack - returns a list of the actions performed
def runaStar(length, numColors, gridSpace, startingPoints, endingPoints):

    color = 0
    startingNodes = []
    solutions = []
    stackTrace = []
    while(color < numColors):
        xcoord = startingPoints[color][0]
        ycoord = startingPoints[color][1]
        ID = str(ycoord) + " " + str(xcoord)
        newNode = node(None, None, xcoord, ycoord, gridSpace[xcoord][ycoord], 0, ID)
        startingNodes.append(newNode)
        color += 1
    color = 0
    while(color < numColors):
        xcoord = endingPoints[color][0]
        ycoord = endingPoints[color][1]
        ID = str(ycoord) + " " + str(xcoord)
        newNode = node(None, None, xcoord, ycoord, gridSpace[xcoord][ycoord], 0, ID)
        startingNodes.append(newNode)
        color += 1

    return aStar(startingNodes, gridSpace, length, numColors)