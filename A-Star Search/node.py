# Name: node.py
# Programmer: Joshua Brinkman
# Date: 2/17/2016
# Requires: none


class node(object):
    # node takes in the parentNode, the action (0-3) taken, the new x/y coordinates, the contents of the cell, the total pathcost, and the node's ID number.
    # this barebones constructor is used to allow the creation of the initial nodes (which have no parent)
    # the makeNode function is used for generating all nodes after that
    def __init__(self, parentNode, action, xcoord, ycoord, contents, pathcost, ID):
        self.parentNode = parentNode
        self.action = action
        self.xcoord = xcoord
        self.ID = ID
        self.children =[]
        self.heuristic = None
        self.ycoord = ycoord
        self.contents = contents
        self.pathcost = pathcost
        self.goalNode = None
    # Appends a child node to the list of child nodes
    def add_child(self, obj):
        self.children.append(obj)
    def set_goal(self, obj):
        self.goalNode = obj
    def set_heuristic(self, obj):
        self.heuristic = abs(self.xcoord - obj.xcoord) + abs(self.ycoord - obj.ycoord)
    def __eq__(self, other):
        if isinstance(other, node):
            return self.ID == other.ID
        return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    # Less than and greater than have been modifed to take the difference in
    # path cost account when comparing two nodes
    def __lt__(self, other):
        if isinstance(other, node):
            return self.heuristic + self.pathcost < other.heuristic + other.pathcost
        return NotImplemented
    def __gt__(self, other):
        if isinstance(other, node):
            return self.heuristic + self.pathcost > other.heuristic + other.pathcost

# Function to easily create a new node, using the properties of a parent node
def makeNode(parentNode, action, gridSpace):

    #0 = up
    #1 = right
    #2 = down
    #3 = left
    mapX = [0,1,0,-1]
    mapY = [1,0,-1,0]
    xcoord = parentNode.xcoord + mapX[action]
    ycoord = parentNode.ycoord + mapY[action]
    contents = parentNode.contents
    ID = str(ycoord) + " " + str(xcoord)
    pathcost = parentNode.pathcost + 1

    # Uses the base node constructor to make a new node
    newNode = node(parentNode, action, xcoord, ycoord, contents, pathcost, ID)
    newNode.set_goal(parentNode.goalNode)
    newNode.set_heuristic(newNode.goalNode)
    parentNode.add_child(newNode)

    return newNode