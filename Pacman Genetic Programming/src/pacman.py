import random, configparser, time, sys, shutil
from actors import *
from EvalTree import *



# Max Depth = 5
# Mu = 40
# 40/(5-1) = 4 groups of 10 each.
# 5 using full, 5 using grow
# This makes the math work out nicely.
def initializePopulation(pacMu,ghostMu,maxDepth,Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient):
    pacSubsets = []
    ghostSubsets = []
    pacPopulation = []
    ghostPopulation = []
    for i in range(maxDepth-1):
        pacRootList = []
        ghostRootList = []
        for j in range(int(pacMu/(maxDepth-1))):
            pacRootList.append(TreeNode(None,None))
        for j in range(int(ghostMu/(maxDepth-1))):
            ghostRootList.append(TreeNode(None,None))
        pacSubsets.append(pacRootList)
        ghostSubsets.append(ghostRootList)

    for i in range(len(pacSubsets)):
        flag = True
        for j in pacSubsets[i]:
            if(flag):
                full(j,0,maxDepth-i,True)
                flag = False
            else:
                grow(j,0,maxDepth-i,True)
                flag = True
    pacRootList = sum(pacSubsets,[])

    for i in range(len(ghostSubsets)):
        flag = True
        for j in ghostSubsets[i]:
            if(flag):
                full(j,0,maxDepth-i,False)
                flag = False
            else:
                grow(j,0,maxDepth-i,False)
                flag = True
    ghostRootList = sum(ghostSubsets,[])

    ghostTreeList = []
    pacTreeList = []

    for i in pacRootList:
        pacTreeList.append(GeneticTree(i,None,''))
    for i in ghostRootList:
        ghostTreeList.append(GeneticTree(i,None,''))


    for controller in pacTreeList:
        board = generateBoard(Height, Width)
        board, pacman, ghosts = placeActors(board, Height, Width)
        board, walls, pills = validateBoard(board, Height, Width, Wall, Pill, pacman, ghosts)
        enemy = random.choice(ghostTreeList)
        fitness, worldString = runPacman(board, Height, Width, pacman, ghosts, pills, Time, timeMult, walls, fruitProb, fruitScore, controller.root, enemy.root)
        controller.fitness = fitness
        controller.worldString = worldString
        if(enemy.used):
            enemy.fitness = float(enemy.fitness - fitness)/2
        else:
            enemy.fitness = -fitness
        enemy.worldString = worldString
        enemy.used = True

    for enemy in ghostTreeList:
        if(not enemy.used):
            board = generateBoard(Height, Width)
            board, pacman, ghosts = placeActors(board, Height, Width)
            board, walls, pills = validateBoard(board, Height, Width, Wall, Pill, pacman, ghosts)
            controller = random.choice(pacTreeList)
            fitness, worldString = runPacman(board, Height, Width, pacman, ghosts, pills, Time, timeMult, walls, fruitProb, fruitScore, controller.root, enemy.root)
            enemy.fitness = -fitness
            enemy.worldString = worldString
            if(controller.used):
                controller.fitness = float(controller.fitness + fitness)/2
            else:
                controller.fitness = fitness
            controller.worldString = worldString
            enemy.used = True
            controller.used = True

    #toggles the used bit
    for i in ghostTreeList:
        i.used = False
        i.fitness = i.fitness - size(i.root,0)*ghostPressureCoefficient

    for i in pacTreeList:
        i.used = False
        i.fitness = i.fitness - size(i.root,0)*pacPressureCoefficient

    return pacTreeList, ghostTreeList


def spawnFruit(board, Height, Width, fruitProb, fruit):
    if random.random() <= fruitProb and fruit == None:
        attempts = 0
        start = 'w'
        while(start !=  '.'):
            y = random.randint(0,Height-1)
            x = random.randint(0,Width-1)
            start = board[y][x]
            attempts += 1
            if(attempts == Height*Width):
                return board, fruit
        board[y][x] = 'f'
        fruit = Fruit(x, y)
        return board, fruit
    return board, fruit


def iterateTurn(board, MsPac, ghostList, pillList, fruit, fruitScore, pacRoot, ghostRoot):
    additional = 0

    for ghost in ghostList:
        actionList = []
        ghost.setCurrentPos()
        for i in range(4):
            acceptable = ghost.TmpMove(board,i)
            if(acceptable):
                fitness = performOperations(ghostRoot, pillList, ghostList, board, fruit, MsPac,ghost)
                actionList.append((i,fitness))
        actionList.sort(key=lambda x: x[1])
        action = actionList[-1][0]
        ghost.move(board,action)

    actionList = []
    MsPac.setCurrentPos()
    for i in range(5):
        acceptable = MsPac.TmpMove(board,i)
        if(acceptable):
            fitness = performOperations(pacRoot, pillList, ghostList, board, fruit, MsPac, ghost)
            actionList.append((i,fitness))
    actionList.sort(key=lambda x: x[1])
    action = actionList[-1][0]

    MsPac.move(board, action)

    if MsPac in ghostList:
        return (True, additional, fruit, pillList)
    for i in pillList:
        if(MsPac == i):
            pillList.remove(i)
            break
    if(MsPac == fruit):
        fruit = None
        additional = fruitScore
    return(False, additional, fruit, pillList)

def generateBoard(Height, Width):
    i = 0
    board = []
    while i < Height:
        j = 0
        row = []
        while j < Width:
            row.append("w")
            j += 1
        board.append(row)
        i += 1
    return board


def findPath(board, start, end):
    while start[0] != end[0]:
        board[start[1]][start[0]] = '.'
        if(end[0] > start[0]):
            start[0] += 1
        else:
            start[0] -= 1
    while start[1] != end[1]:
        board[start[1]][start[0]] = '.'
        if(end[1] > start[1]):
            start[1] += 1
        else:
            start[1] -= 1


def validateBoard(board, Height, Width, WallDensity, PillDensity, pacman, ghosts):
    pills = []
    walls = []
    randomEnd = [pacman] + ghosts

    WallExpectedValue = max(1,WallDensity*(Height*Width-2))
    numWalls = random.gauss(WallExpectedValue, 0.05*(Height*Width-2))

    PillExpectedValue = max(1,PillDensity*(Height*Width - 1 - numWalls))
    numPills = random.gauss(PillExpectedValue, 0.05*(Height*Width - 1 - numWalls))

    for i in ghosts:
        findPath(board,[pacman[1],pacman[2]],[i[1],i[2]])
    while(sum(z.count('w') for z in board) > numWalls):
        start = 'w'
        while start == 'w':
            y = random.randint(0,Height-1)
            x = random.randint(0,Width-1)
            startingPoint = [x,y]
            start = board[y][x]

        start = 'm'
        while start != 'w':
            y = random.randint(0,Height-1)
            x = random.randint(0,Width-1)
            endingPoint = [x,y]
            start = board[y][x]

        findPath(board,startingPoint,endingPoint)

    board[pacman[2]][pacman[1]] = pacman[0]

    for i in ghosts:
        board[i[2]][i[1]] = str(i[0])

    placedPills = 0
    while(placedPills < numPills):
        start = 'm'
        while start != '.':
            y = random.randint(0,Height-1)
            x = random.randint(0,Width-1)
            start = board[y][x]
        board[y][x] = 'p'
        pills.append(('p',x,y))
        placedPills += 1

    i = 0
    while i < Height:
        j = 0
        while j < Width:
            if(board[i][j] == 'w'):
                walls.append(('w',j,i))
            j += 1
        i += 1

    return board, walls, pills


def placeActors(board, Height, Width):
    ghosts = []
    board[0][0] = "m"
    pacman = ('m',0,0)
    board[-1][-1] = 1
    ghosts.append((1,len(board[-1])-1,len(board)-1))
    board[-2][-1] = 2
    ghosts.append((2,len(board[-1])-2,len(board)-1))
    board[-1][-2] = 3
    ghosts.append((3,len(board[-1])-1,len(board)-2))
    return board, pacman, ghosts

# Function to run the entire pacman game. Returns the score, and the move string.
def runPacman(board, Height, Width, pacman, ghosts, pills, Time, timeMult, walls, fruitProb, fruitScore,pacRoot, ghostRoot):
    score = 0
    worldList = []
    ghostList = []
    pillList = []
    MsPac = MsPacman(pacman[1],pacman[2])
    for j in ghosts:
        ghostList.append(ghost(j[1],j[2],j[0]))
    for k in pills:
        pillList.append(Pill(k[1],k[2]))

    worldList.append(str(Width))
    worldList.append("\n")
    worldList.append(str(Height))
    worldList.append("\n")
    worldList.append("%s %d %d \n" %(pacman[0],pacman[1],pacman[2]))
    for j in ghosts:
         worldList.append("%d %d %d \n" %(j[0],j[1],j[2]))
    for k in walls:
         worldList.append("%s %d %d \n" %(k[0],k[1],k[2]))
    for l in pills:
         worldList.append("%s %d %d \n" %(l[0],l[1],l[2]))
    worldList.append("%s %d %d \n" %('t',Time,score))
    fruit = None
    pillDenom = len(pillList)
    fruitPoints = []
    for j in range(Time):
        board, fruit = spawnFruit(board, Height, Width, fruitProb, fruit)

        gameOver, additional, fruit, pillList = iterateTurn(board, MsPac, ghostList, pillList, fruit, fruitScore, pacRoot, ghostRoot)

        fruitPoints.append(additional)
        worldList.append("%s %d %d \n" %('m',MsPac.xCoord,MsPac.yCoord))
        for k in ghostList:
             worldList.append("%d %d %d \n" %(k.label,k.xCoord,k.yCoord))
        if(fruit != None):
            worldList.append("%s %d %d \n" %('f',fruit.xCoord,fruit.yCoord))
        score = int(100*(1 - float(len(pillList))/pillDenom)) + sum(fruitPoints)
        worldList.append("%s %d %d \n" %('t',Time-j,score))
        if(gameOver):
            score -= int(100*(1 - float(j)/Time))
            break
        if(len(pillList) == 0):
            score += int(100*(1 - float(j)/Time))
            break
    return (score,worldList)

# Deep copies parents prior to mutation and crossover, to ensure they're preserved.
# Crossover Rate = 100%, Mutation Rate = 5%
# Parsimony based on number of nodes in the tree
# Returns 1 child
def generateChild(parent1, parent2, pressureCoefficient, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore,enemy,player):
    child1 = deepTreeCopy(parent1,None)
    child2 = deepTreeCopy(parent2,None)
    crossoverSubTree(randomSubTree(child1),randomSubTree(child2))
    tmp = [child1, child2]
    child = random.choice(tmp)

    if(random.random() < 0.05):
        mutate(child,player)

    return GeneticTree(child,None,None)


# A function to pick the p best individuals, and clone them to fill the population
#	Pre: population - an array of mu individuals
#		 pop_size - mu
#		 p - number of survivors
#
#	Post: population with pop_size/p copies of the best individuals
def truncation(population, pop_size, p):
    population.sort()
    numClones = int(pop_size/p)

    survivors = population[-p:]
    population = []
    for i in range(0,numClones):
        population += survivors

    if(len(population) != pop_size):
        print("WARNING! EXPECTED SIZE: ", pop_size, " ACTUAL: ", len(population))

    return population

# A function to simulate Roulette Selection
#	Pre: Population - an array of mu individuals
#		 MAX - True to find best individual, False to find worst
#
#	Post: a random indivudal with a specified weight
def rouletteSelection(population, MAX):
    fitness = [i.fitness for i in population]

    minFS = min(fitness)
    for i in fitness:
        i += minFS
        #Normalize the fitness values
    sumFS = sum(fitness)
    maxFS = max(fitness)
    minFS = min(fitness)
    p = random.random()*sumFS
    t = maxFS + minFS
    chosen = population[0]
    for i in population:
        if MAX:
            p -= i.fitness
        else:
            p -= (t - i.fitness)
        if p < 0:
            chosen = i
            break
    return i

# A function to sample k random individuals in the population, and return the best
#	Pre: population - an array of Mu Individuals
#	     k - the numbers of samplings before returning a result
#		 replacement - boolean determining if you do/do not replace after selection
#
#	Post: best - the most fit individual from the subset of k idividuals
def tournament_selection(population, k):
	best = False
	for i in range(0,k):
		choice = random.choice(population)
		if(best != False):
			if(choice > best):
				best = choice
		else:
			best = choice
	return best

# A function to over select
# Divides the population into the top 20% and bottom 80%
# 80% of the time, selects from top 20%
def overselect(population,Overselect):
    mu = len(population)
    population.sort()

    divide = int(mu*Overselect)

    top = population[divide:]
    bottom = population[:divide]

    for i in range(mu):
        if(random.randint(1,10) < 9):
            return random.choice(top)
        else:
            return random.choice(bottom)

def iteratePacmanGeneration(pacPopulation, ghostPopulation, pac_gen_size, pac_pop_size, pac_survival_size, pacParentType, pacSurvivalType, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient, Overselect):
    children = []
    for i in range(0,pac_gen_size):
        if(pacParentType == 0):
			#fitness proportional selection
            parent1 = rouletteSelection(pacPopulation, True).root
            parent2 = rouletteSelection(pacPopulation, True).root
            child = generateChild(parent1, parent2, pacPressureCoefficient, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, random.choice(ghostPopulation).root, True)
            children.append(child)

        if(pacParentType == 1):
			#over selection
            parent1 = overselect(pacPopulation,Overselect).root
            parent2 = overselect(pacPopulation,Overselect).root
            child = generateChild(parent1, parent2, pacPressureCoefficient, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, random.choice(ghostPopulation).root, True)
            children.append(child)
    pacChildren = children

    return pacPopulation + pacChildren

def iterateGhostGeneration(pacPopulation, ghostPopulation, ghost_gen_size, ghost_pop_size, ghost_survival_size, ghostParentType, ghostSurvivalType, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient, Overselect):
    children = []

    for i in range(0,ghost_gen_size):
        if(ghostParentType == 0):
			#fitness proportional selection
            parent1 = rouletteSelection(ghostPopulation, True).root
            parent2 = rouletteSelection(ghostPopulation, True).root
            child = generateChild(parent1, parent2, ghostPressureCoefficient, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, random.choice(pacPopulation).root, False)
            children.append(child)

        if(ghostParentType == 1):
			#over selection
            parent1 = overselect(ghostPopulation,Overselect).root
            parent2 = overselect(ghostPopulation,Overselect).root
            child = generateChild(parent1, parent2, ghostPressureCoefficient, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, random.choice(pacPopulation).root, False)
            children.append(child)

    ghostChildren = children

    return ghostPopulation + ghostChildren

# Finds individual with best fitness, and calls avgPopFitness
#        Pre: population - list of Mu individuals
#             pop_size - size of population (Mu)
#
#        Post: bestFitness - most fit individual in the population
#                  avgFitness - the result returned from avgPopFitness
def processPopulation(pacPopulation, ghostPopulation, pac_pop_size):
        avg = 0
        bestPac = GeneticTree(None,-9999,'')
        bestGhost = GeneticTree(None,-9999,'')
        for i in pacPopulation:
                avg += i.fitness
                if(i.fitness > bestPac.fitness):
                    bestPac = i
        for i in ghostPopulation:
                if(i.fitness > bestGhost.fitness):
                    bestGhost = i
        return bestPac,bestGhost,avg/float(pac_pop_size)

# Finds the average fitness of the population
#        Pre: population - list of Mu individuals
#             pop_size - size of population (Mu)
#
#        Post: sum of population fitness, divided by Mu

def EVOLVE_OR_DIE(NumEvals, pac_pop_size, pac_gen_size, pac_survival_size, ghost_pop_size, ghost_gen_size, ghost_survival_size, terminator, pacParentType, pacSurvivalType, ghostParentType, ghostSurvivalType, Height, Width, Pill, Time, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient, Overselect):
        noAvgChange = 0
        noBestChange = 0
        logList = []

        #Initialize population, bestPacFitness, bestGhostFitness and avgPacFitness
        pacPopulation, ghostPopulation = initializePopulation(pac_pop_size, ghost_pop_size, 5, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore,pacPressureCoefficient,ghostPressureCoefficient)

        bestPac, bestGhost, avgFitness = processPopulation(pacPopulation,ghostPopulation,pac_pop_size)

        prevBestPac = bestPac.fitness
        prevBestGhost = bestGhost.fitness
        prevAvg = avgFitness

        logList.append("%d	%f	%f \n" % (pac_pop_size,avgFitness,bestPac.fitness))

        i = pac_pop_size
        while(i <= NumEvals):
                if(len(pacPopulation) != pac_pop_size):
                    print("Pac: Expected ", pac_pop_size, " Actual ", len(pacPopulation))
                if(len(ghostPopulation) != ghost_pop_size):
                    print("Ghost: Expected ", ghost_pop_size, " Actual ", len(pacPopulation))
                generation = False
                pacPopulation = iteratePacmanGeneration(pacPopulation, ghostPopulation, pac_gen_size, pac_pop_size, pac_survival_size, pacParentType, pacSurvivalType, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient,Overselect)

                ghostPopulation = iterateGhostGeneration(pacPopulation, ghostPopulation, ghost_gen_size, ghost_pop_size, ghost_survival_size, ghostParentType, ghostSurvivalType, Height, Width, Pill, Time, NumEvals, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient,Overselect)

                generation = True

                if(generation):

                    for controller in pacPopulation:
                        enemy = random.choice(ghostPopulation)
                        seekTime = time.time()
                        while(enemy.used):
                            enemy = random.choice(ghostPopulation)
                            if(time.time() - seekTime > 0.5):
                                break
                        board = generateBoard(Height, Width)
                        board, pacman, ghosts = placeActors(board, Height, Width)
                        board, walls, pills = validateBoard(board, Height, Width, Wall, Pill, pacman, ghosts)
                        fitness, worldString = runPacman(board, Height, Width, pacman, ghosts, pills, Time, timeMult, walls, fruitProb, fruitScore, controller.root, enemy.root)
                        controller.fitness = fitness
                        controller.worldString = worldString
                        if(enemy.used):
                            enemy.fitness = float(enemy.fitness - fitness)/2
                        else:
                            enemy.fitness = -fitness
                        enemy.worldString = worldString
                        enemy.used = True
                        i += 1
                    for enemy in ghostPopulation:
                        if(not enemy.used):
                            board = generateBoard(Height, Width)
                            board, pacman, ghosts = placeActors(board, Height, Width)
                            board, walls, pills = validateBoard(board, Height, Width, Wall, Pill, pacman, ghosts)
                            fitness, worldString = runPacman(board, Height, Width, pacman, ghosts, pills, Time, timeMult, walls, fruitProb, fruitScore, controller.root, enemy.root)
                            controller.fitness = float(controller.fitness + fitness)/2
                            enemy.fitness = -fitness
                            enemy.worldString = worldString
                            controller.worldString = worldString
                            i += 1
                    for a in ghostPopulation:
                        a.used = False
                        a.fitness = a.fitness - size(a.root,0)*ghostPressureCoefficient
                    for b in pacPopulation:
                        b.fitness = b.fitness - size(b.root,0)*pacPressureCoefficient

                    #truncation
                    if(pacSurvivalType == 0):
                        pacPopulation = truncation(pacPopulation, pac_pop_size, 5)

                	#k-tournament w/o replacement
                    if(pacSurvivalType == 1):
                        survivors = []
                        for j in range(0,pac_gen_size):
                            result = tournament_selection(pacPopulation, pac_survival_size)
                            survivors.append(result)
                            pacPopulation.remove(result)

                        for l in range (0, pac_gen_size):
                            candidate = random.choice(pacPopulation)
                            pacPopulation.remove(candidate)
                        pacPopulation += survivors

                   	#truncation
                    if(ghostSurvivalType == 0):
                        ghostPopulation = truncation(ghostPopulation, ghost_pop_size, 5)

                	#k-tournament w/o replacement
                    if(ghostSurvivalType == 1):
                        survivors = []
                        for j in range(0,ghost_gen_size):
                            result = tournament_selection(ghostPopulation, ghost_survival_size)
                            survivors.append(result)
                            ghostPopulation.remove(result)

                        for l in range (0, ghost_gen_size):
                            candidate = random.choice(ghostPopulation)
                            ghostPopulation.remove(candidate)
                        ghostPopulation += survivors

                    bestPac, bestGhost, avgFitness = processPopulation(pacPopulation,ghostPopulation,pac_pop_size)
                    bestPacFitness = bestPac.fitness
                    bestGhostFitness = bestGhost.fitness
                    if(prevBestPac == bestPacFitness):
                            noBestChange += 1
                    elif(prevBestGhost == bestGhostFitness):
                        noBestChange +=1
                    else:
                        noBestChange = 0
                    if(prevAvg == avgFitness):
                            noAvgChange += 1
                    else:
                            noAvgChange = 0

                    logList.append("%d  %f	%f \n" %(i,avgFitness,bestPacFitness))

                    if(noBestChange == terminator or noAvgChange == terminator):
                            break
                    prevAvg = avgFitness
                    prevBestPac = bestPacFitness
                    prevBestGhost = bestGhostFitness




        bestPac, bestGhost, avgFitness = processPopulation(pacPopulation,ghostPopulation,pac_pop_size)

        return bestPac, bestGhost, logList

def main():
    configParser = configparser.RawConfigParser()
    if(len(sys.argv) != 2):
        configParser.read("./configurations/default.cfg")
        path = "./configurations/default.cfg"
    else:
        configParser.read(sys.argv[1])
        path = sys.argv[1]

    #Read in all the values from the config file

    Height = int(configParser.get('my-config', 'Height'))
    Width = int(configParser.get('my-config', 'Width'))
    Wall = float(configParser.get('my-config', 'WallDensity'))
    Pill = float(configParser.get('my-config', 'PillDensity'))
    fruitProb = float(configParser.get('my-config', 'FruitProb'))
    fruitScore = int(configParser.get('my-config','FruitScore'))
    timeMult = int(configParser.get('my-config','TimeMultiplier'))
    LogOutput = configParser.get('my-config', 'LogOutput')
    NumRuns = int(configParser.get('my-config', 'NumRuns'))
    NumEvals = int(configParser.get('my-config', 'NumEvals'))
    Timer = bool(configParser.get('my-config', 'Timer'))
    GameOutput = configParser.get('my-config', 'GameOutput')
    PacSolutionOutput = configParser.get('my-config', 'PacSolutionOutput')
    GhostSolutionOutput = configParser.get('my-config', 'GhostSolutionOutput')
    pac_pop_size = int(configParser.get('my-config', 'Pac_Mu'))
    pac_gen_size = int(configParser.get('my-config', 'Pac_Lambda'))
    pacParentType = int(configParser.get("my-config",'Pac_Parent'))
    pacSurvivalType = int(configParser.get('my-config','Pac_Survival'))
    pac_survival_size = int(configParser.get('my-config', 'Pac_SurvivalK'))
    ghost_pop_size = int(configParser.get('my-config', 'Ghost_Mu'))
    ghost_gen_size = int(configParser.get('my-config', 'Ghost_Lambda'))
    ghostParentType = int(configParser.get("my-config",'Ghost_Parent'))
    ghostSurvivalType = int(configParser.get('my-config','Ghost_Survival'))
    ghost_survival_size = int(configParser.get('my-config', 'Ghost_SurvivalK'))
    terminator = int(configParser.get('my-config', 'Nval'))
    pacPressureCoefficient = float(configParser.get("my-config", "Pac_Parsimony"))
    ghostPressureCoefficient = float(configParser.get("my-config", "Ghost_Parsimony"))
    Overselect = float(configParser.get("my-config", "Overselect"))

    #initialize output files
    myfile =  open(LogOutput, "w+")
    myfile.close()

    if(Timer):
            seedValue = time.time()
            random.seed(seedValue)
    else:
            random.seed(int(configParser.get('my-config', 'TimerSeed')))

    with open(LogOutput, "a") as myfile:
            myfile.write("Result Log \n")
            myfile.write("Config file path: %s \n" %(path))
            myfile.write("Using Timer Initialized Seed: %r \n" %(Timer,))
            myfile.write("Random seed value: %d \n" %(seedValue,))
            myfile.write("Height: %d \n" %(Height,))
            myfile.write("Width: %d \n" %(Width,))
            myfile.write("Pill Density: %f \n" %(Pill,))
            myfile.write("Wall Density: %f \n" %(Wall,))
            myfile.write("Fruit Probability: %f \n" %(fruitProb,))
            myfile.write("Fruit Value: %d \n" %(fruitScore,))
            myfile.write("Pac Mu: %d \n" %(pac_pop_size,))
            myfile.write("Pac Lambda: %d \n" %(pac_gen_size,))
            myfile.write("Pac Initialization scheme: Ramped Half-Half \n")
            myfile.write("Pac Parent selection scheme: %d \n" %(pacParentType,))
            myfile.write("Pac Survivor selection scheme: %d \n" %(pacSurvivalType,))
            myfile.write("Pac Survivor k-tournament: %d \n" %(pac_survival_size,))
            myfile.write("Ghost Mu: %d \n" %(ghost_pop_size,))
            myfile.write("Ghost Lambda: %d \n" %(ghost_gen_size,))
            myfile.write("Ghost Initialization scheme: Ramped Half-Half \n")
            myfile.write("Ghost Parent selection scheme: %d \n" %(ghostParentType,))
            myfile.write("Ghost Survivor selection scheme: %d \n" %(ghostSurvivalType,))
            myfile.write("Ghost Survivor k-tournament: %d \n" %(ghost_survival_size,))
            myfile.write("Terminate on no average Fitness change: True \n")
            myfile.write("Terminate on no best Fitness change: True \n")
            myfile.write("Number of generations to terminate on no best/avg change: %d \n" %(terminator,))
            myfile.write("Number of runs: %d \n" %(NumRuns))
            myfile.write("Number of evals: %d \n" %(NumEvals))
            myfile.write("\n")

    Time = Height*Width*timeMult

    bestGhosts =[]
    bestPacmen = []
    for j in range(NumRuns):
        with open(LogOutput, "a") as myfile:
            myfile.write("Run " + str(j+1) + "\n")
        print("Run: ", j+1)
        bestPac, bestGhost, logList = EVOLVE_OR_DIE(NumEvals, pac_pop_size, pac_gen_size, pac_survival_size, ghost_pop_size, ghost_gen_size, ghost_survival_size, terminator, pacParentType, pacSurvivalType, ghostParentType, ghostSurvivalType, Height, Width, Pill, Time, timeMult, Wall, fruitProb, fruitScore, pacPressureCoefficient, ghostPressureCoefficient, Overselect)
        with open(LogOutput, "a") as myfile:
            myfile.write(''.join(logList))
        bestPacmen.append((bestPac, bestPac.fitness))
        bestGhosts.append((bestGhost,bestGhost.fitness))

    bestPacmen.sort(key=lambda x: x[1])
    bestGhosts.sort(key=lambda x: x[1])
    bestFile = ''.join(bestPacmen[-1][0].worldString)
    with open(GameOutput, "w+") as myfile:
        myfile.write(bestFile)
    with open(PacSolutionOutput, "w+") as myfile:
        myfile.write(' '.join(map(str, inOrderPrint(bestPacmen[-1][0].root))))
    with open(GhostSolutionOutput, "w+") as myfile:
        myfile.write(' '.join(map(str, inOrderPrint(bestGhosts[-1][0].root))))


if __name__ == '__main__':
    main()
