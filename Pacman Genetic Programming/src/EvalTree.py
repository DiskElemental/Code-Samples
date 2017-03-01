import random
from actors import *

#Wrapper class, points to the root node of the tree and contains the fitness of this controller.
class GeneticTree(object):
    used = False

    def __init__(self,root,fitness,worldString):
        self.root = root
        self.fitness = fitness
        self.worldString = worldString

    def __eq__(self, other):
                if isinstance(other, GeneticTree):
                        return self.fitness == other.fitness
                return NotImplemented
    def __ne__(self, other):
            result = self.__eq__(other)
            if result is NotImplemented:
                    return result
            return not result

    def __lt__(self, other):
            if isinstance(other, GeneticTree):
                    return self.fitness < other.fitness
            return NotImplemented
    def __gt__(self, other):
            if isinstance(other, GeneticTree):
                    return self.fitness > other.fitness

#Simple node to use in the binary tree
class TreeNode(object):
    left = None
    right = None

    def __init__(self,parent,contents):
        self.parent = parent
        self.contents = contents

    def addChild(self,left,right):
        self.left = left
        self.right = right

def deepTreeCopy(root,parent):
    if root == None:
        return None
    copy = TreeNode(parent,root.contents)
    copy.addChild(deepTreeCopy(root.left,copy),deepTreeCopy(root.right,copy))
    return copy

def validateTree(root):
    non_terminals = ["ADD", "SUB","DIV","MUL","RAND"]
    terminals =["pill","ghost","wall","fruit","pac"]
    if root == None:
        return True
    if(root.contents in terminals and (root.left != None or root.right != None)):
        return False
    if(root.left == None and root.right == None and root.contents in non_terminals):
        return False
    if(root.left == None and root.right != None):
        return False
    if(root.left != None and root.right == None):
        return False
    left = validateTree(root.left)
    right = validateTree(root.right)
    return(left and right)

def crossoverSubTree(root,otherRoot):
    tmp = root.parent
    root.parent = otherRoot.parent
    otherRoot.parent = tmp
    if(otherRoot.parent != None):
        if(otherRoot.parent.left == root):
            otherRoot.parent.left = otherRoot
        else:
            otherRoot.parent.right = otherRoot

    if(root.parent != None):
        if (root.parent.left == otherRoot):
            root.parent.left = root
        else:
            root.parent.right = root

def makeTmpList(node):
    if node is None:
        return []
    return makeTmpList(node.left) + [node] + makeTmpList(node.right)

def randomSubTree(node):
    return random.choice(makeTmpList(node))

def inOrderPrint(node):
    if node is None:
        return []
    return inOrderPrint(node.left) + [node.contents] + inOrderPrint(node.right)

def size(node, current):
    if node == None:
        return current
    return size(node.left, current) + 1 + size(node.right, current)

class DataCache(object):
    pill = None
    ghost = None
    fruit = None
    wall = None
    pac = None

def performOperations(node, pillList, ghostList, board, fruit, pacman,subject):
    cache = DataCache()
    return RunTree(node, pillList, ghostList, board, fruit, pacman,subject,cache)

def RunTree(node, pillList, ghostList, board, fruit, pacman,subject,cache):
    if(node.contents == "pill"):
        if(cache.pill == None):
            val = PillSensor(pillList,subject)
            cache.pill = val
            return val
        else:
            return cache.pill
    if(node.contents == "ghost"):
        if(cache.ghost == None):
            val = GhostSensor(ghostList,subject)
            cache.ghost = val
            return val
        else:
            return cache.ghost
    if(node.contents == "fruit"):
        if(cache.fruit == None):
            val = FruitSensor(fruit,subject)
            cache.fruit = val
            return val
        else:
            return cache.fruit
    if(node.contents == "wall"):
        if(cache.wall == None):
            val = WallSensor(board,subject)
            cache.wall = val
            return val
        else:
            return cache.wall
    if(node.contents == "pac"):
        if(cache.pac == None):
            val = PacSensor(subject,pacman)
            cache.pac = val
            return val
        else:
            return cache.pac
    if(node.left == None or node.right == None):
        return node.contents
    leftVal = RunTree(node.left, pillList, ghostList, board, fruit, pacman,subject,cache)
    rightVal = RunTree(node.right, pillList, ghostList, board, fruit, pacman,subject,cache)
    if(node.contents == "ADD"):
        return leftVal + rightVal
    if(node.contents == "SUB"):
        return leftVal - rightVal
    if(node.contents == "DIV"):
        try:
            return leftVal / rightVal
        except ZeroDivisionError:
            return float("inf")
    if(node.contents == "MUL"):
        return leftVal * rightVal
    if(node.contents == "RAND"):
        return random.uniform(leftVal,rightVal)


#Can take in any node in the tree
#Initial depth previously calculated
#max depth determined by initial
#player True = Pacman, Terminals
#player False = ghost, ghostTerminals
def grow(node, depth, maxDepth, player):
    non_terminals = ["ADD", "SUB","DIV","MUL","RAND"]
    terminals =["pill","ghost","wall","fruit", "num"]
    ghostTerminals =["pac","ghost", "num"]
    # 50/50 chance of going deeper, or staying the same
    thing = random.randint(0,1)
    if(thing == 0 and depth != maxDepth):
        node.contents = random.choice(non_terminals)
        leftChild = TreeNode(node, None)
        rightChild = TreeNode(node,None)
        grow(leftChild,depth+1,maxDepth,player)
        grow(rightChild,depth+1,maxDepth,player)
        node.addChild(leftChild,rightChild)
    else:
        if(player):
            node.contents = random.choice(terminals)
            if(node.contents == "num"):
                node.contents = random.uniform(0,10)
        else:
            node.contents = random.choice(ghostTerminals)
            if(node.contents == "num"):
                node.contents = random.uniform(0,10)
        node.addChild(None,None)

def full(node,depth,maxDepth,player):
    non_terminals = ["ADD", "SUB","DIV","MUL","RAND"]
    terminals =["pill","ghost","wall","fruit", "num"]
    ghostTerminals =["pac","ghost", "num"]
    if depth != maxDepth:
        node.contents = random.choice(non_terminals)
        leftChild = TreeNode(node, None)
        rightChild = TreeNode(node,None)
        full(leftChild,depth+1,maxDepth,player)
        full(rightChild,depth+1,maxDepth,player)
        node.addChild(leftChild,rightChild)
    else:
        if(player):
            node.contents = random.choice(terminals)
            if(node.contents == "num"):
                node.contents = random.uniform(0,10)
        else:
            node.contents = random.choice(ghostTerminals)
            if(node.contents == "num"):
                node.contents = random.uniform(0,10)
        node.addChild(None,None)

def mutate(root,player):
    node = randomSubTree(root)
    depth = 0
    tmp = node
    while tmp.parent != None:
        depth +=1
        tmp = tmp.parent
    grow(node,depth,25,player)




