import random, math

class MsPacman(object):

    actions = [(-1,0), (0,1),(1,0),(0,-1),(0,0)]

    def __init__(self, xCoord, yCoord):
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.previousX = xCoord
        self.previousY = yCoord
        self.actualCoords = (xCoord,yCoord)

    #returns True if the given action is valid, false otherwise
    def move(self, board, action):
        if((self.xCoord,self.yCoord) != self.actualCoords):
            self.xCoord, self.yCoord = self.actualCoords
        move = self.actions[action]
        tmpX = self.xCoord + move[1]
        tmpY = self.yCoord + move[0]
        if(((-1 < tmpX and tmpX < len(board[0])) and (-1 < tmpY and tmpY < len(board)))):
            if(board[tmpY][tmpX] != 'w'):
                self.previousX = self.xCoord
                self.previousY = self.yCoord
                self.xCoord = tmpX
                self.yCoord = tmpY
                board[self.yCoord][self.xCoord] = 'm'
                board[self.previousY][self.previousX] = '.'
                return True
            else:
                return False
        else:
            return False

    def TmpMove(self,board,action):
        if((self.xCoord,self.yCoord) != self.actualCoords):
            self.xCoord, self.yCoord = self.actualCoords
        move = self.actions[action]
        tmpX = self.xCoord + move[1]
        tmpY = self.yCoord + move[0]
        if(((-1 < tmpX and tmpX < len(board[0])) and (-1 < tmpY and tmpY < len(board)))):
            if(board[tmpY][tmpX] != 'w'):
                self.xCoord = tmpX
                self.yCoord = tmpY
                return True
            else:
                return False
        else:
            return False

    def setCurrentPos(self):
         self.actualCoords = (self.xCoord,self.yCoord)

    def __eq__(self, other):
        #Checks if the previous position of pacman is ghost's current position
        #And if current position of pacman is ghost's previous position
        #If True, then pacman and the ghost collided
        if isinstance(other, ghost):
            return(((self.xCoord == other.previousX) and (self.yCoord == other.previousY) and (self.previousX == other.xCoord) and (self.previousY == other.yCoord)) or ((self.xCoord == other.xCoord and self.yCoord == other.yCoord)))
        if isinstance(other, Pill):
            return(self.xCoord == other.xCoord and self.yCoord == other.yCoord)
        if isinstance(other, Fruit):
            return(self.xCoord == other.xCoord and self.yCoord == other.yCoord)
        return NotImplemented


class ghost(object):
    actions = [(-1,0), (0,1),(1,0),(0,-1)]
    previousContent = '.'


    def __init__(self, xCoord, yCoord, label):
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.previousX = xCoord
        self.previousY = yCoord
        self.label = label
        self.actualCoords = (xCoord,yCoord)

    def move(self, board, action):
        if((self.xCoord,self.yCoord) != self.actualCoords):
            self.xCoord, self.yCoord = self.actualCoords
        self.xCoord = self.previousX
        self.yCoord = self.previousY
        move = self.actions[action]
        tmpX = self.xCoord + move[1]
        tmpY = self.yCoord + move[0]
        board[self.yCoord][self.xCoord] = self.previousContent
        if(((-1 < tmpX and tmpX < len(board[0])) and (-1 < tmpY and tmpY < len(board)))):
            if(board[tmpY][tmpX] != 'w'):
                self.previousX = self.xCoord
                self.previousY = self.yCoord
                self.xCoord = tmpX
                self.yCoord = tmpY
                self.previousContent = board[self.yCoord][self.xCoord]
                board[self.yCoord][self.xCoord] = self.label
                return True
            else:
                return False
        else:
            return False

    def TmpMove(self,board,action):
        if((self.xCoord,self.yCoord) != self.actualCoords):
            self.xCoord, self.yCoord = self.actualCoords
        move = self.actions[action]
        tmpX = self.xCoord + move[1]
        tmpY = self.yCoord + move[0]
        if(((-1 < tmpX and tmpX < len(board[0])) and (-1 < tmpY and tmpY < len(board)))):
            if(board[tmpY][tmpX] != 'w'):
                self.xCoord = tmpX
                self.yCoord = tmpY
                return True
            else:
                return False
        else:
            return False

    def setCurrentPos(self):
        self.actualCoords = (self.xCoord,self.yCoord)

    def __eq__(self, other):
        #Checks if the previous position of pacman is ghost's current position
        #And if current position of pacman is ghost's previous position
        #If True, then pacman and the ghost collided
        if isinstance(other, MsPacman):
            return(((self.xCoord == other.previousX) and (self.yCoord == other.previousY) and (self.previousX == other.xCoord) and (self.previousY == other.yCoord)) or ((self.xCoord == other.xCoord) and (self.yCoord == other.yCoord)))
        if isinstance(other, ghost):
            return((self.xCoord == other.xCoord) and (self.yCoord == other.yCoord))
        return NotImplemented

class Pill(object):

    def __init__(self, xCoord, yCoord):
        self.xCoord = xCoord
        self.yCoord = yCoord

    def __eq__(self, other):
        if isinstance(other, MsPacman):
            return(self.xCoord == other.xCoord and self.yCoord == other.yCoord)
        return NotImplemented

class Fruit(object):
    def __init__(self, xCoord, yCoord):
        self.xCoord = xCoord
        self.yCoord = yCoord

    def __eq__(self, other):
        if isinstance(other, MsPacman):
            return(self.xCoord == other.xCoord and self.yCoord == other.yCoord)
        return NotImplemented

#returns distance to closest pill
def PillSensor(pillList, pacman):
    least = 99999
    for pill in pillList:
        dist = (abs(pill.xCoord - pacman.xCoord) + abs(pill.yCoord - pacman.yCoord))
        if(dist < least):
            dist = least
    return dist

#returns distance to closest ghost
def GhostSensor(ghostList, pacman):
    least = 99999
    dist = 99
    for ghost in ghostList:
        if(pacman != ghost):
            dist = (abs(ghost.xCoord - pacman.xCoord) + abs(ghost.yCoord - pacman.yCoord))
            if(dist < least):
                dist = least
    return dist

#returns distance to fruit
def FruitSensor(fruit, pacman):
    if(fruit != None):
        return (abs(fruit.xCoord - pacman.xCoord) + abs(fruit.yCoord - pacman.yCoord))
    return 0

def PacSensor(subject,pacman):
    return(abs(pacman.xCoord - subject.xCoord) + abs(pacman.yCoord - subject.yCoord))

#returns number of walls adjacent to pacman
def WallSensor(board, pacman):
    numWalls = 0
    try:
        if(board[pacman.yCoord+1][pacman.xCoord] == "w"):
            numWalls += 1
    except IndexError:
        pass
    try:
        if(board[pacman.yCoord-1][pacman.xCoord] == "w"):
            numWalls += 1
    except IndexError:
        pass
    try:
        if(board[pacman.yCoord][pacman.xCoord+1] == "w"):
            numWalls += 1
    except IndexError:
        pass
    try:
        if(board[pacman.yCoord][pacman.xCoord-1] == "w"):
            numWalls += 1
    except IndexError:
        pass

    return numWalls
