# Name: main.py
# Programmer: Joshua Brinkman
# Date: 2/17/2016
# Requires: node.py, aStar.py

import timeit, sys, getopt
from node import *
from aStar import *

def main(argv):

    # Reads in the first two characters of the file, to get the size of grid
    # And number of colors
    try:
        opts, args = getopt.getopt(argv,"hi:o:t:",["ifile=","ofile="])
    except getopt.GetoptError:
        print("main.py -i <inputfile> -o <outputfile> -t <algorithm type, TS/GS>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("main.py -i <inputfile> -o <outputfile> -t <algorithm type, TS/GS>")
            sys.exit()
        elif(opt in ("-i", "--ifile")):
            puzzleName = arg + ".txt"
        elif(opt in ("-o", "--ofile")):
            solutionName = arg + ".txt"

    start = timeit.default_timer()
    puzzle = open(puzzleName, "r")
    line = puzzle.readline()
    length, numColors = line.split()
    length = int(length)
    numColors = int(numColors)
    # Dumps the remainder of the file into a grid
    # Records the x and y coordinates of the first Z unique symbols
    # Where Z is the number of Colors read in above
    gridSpace = [[0 for x in range(length)] for x in range(length)]
    array = puzzle.read()
    iterator1 = 0
    iterator2 = 0
    totalSteps = 0
    foundSymbols = []
    foundEndPoints = []
    tempSymbolStorage = []
    while iterator1 < length:
        iterator2 = 0
        while iterator2 < length:
            gridSpace[iterator1][iterator2] = array[totalSteps]
            if(array[totalSteps] != 'e'):
                if(array[totalSteps] not in tempSymbolStorage):
                    foundSymbols.append([iterator1, iterator2])
                    tempSymbolStorage.append(array[totalSteps])
                elif(array[totalSteps] in tempSymbolStorage):
                    foundEndPoints.append([iterator1, iterator2])
            totalSteps += 2
            iterator2 += 1
        iterator1 += 1
    puzzle.close()

    # Passes the length, number of Colors, the completed grid, and the list of starting locations
    stackTrace = runaStar(length, numColors, gridSpace, foundSymbols, foundEndPoints)
    iterator1 = 0
    solution = open(solutionName, "w")
    #Prints out the required information
    stop = timeit.default_timer()
    print str((stop - start)*1000000) + " micro seconds"
    solution.write(str((stop - start)*1000000) + " micro seconds" + '\n')
    print str(len(stackTrace)) + " steps"
    solution.write((str(len(stackTrace))) + " steps" + '\n')
    for item in stackTrace:
        for index in item:
            solution.write(" " + str(index))
        solution.write(",")
    solution.write('\n')
    while iterator1 < length:
        print(gridSpace[iterator1])
        for item in gridSpace[iterator1]:
            solution.write(" " + str(item))
        solution.write('\n')
        iterator1 += 1
    solution.close()


if __name__ == '__main__':
    main(sys.argv[1:])
