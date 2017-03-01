# Author: Joshua Brinkman
# Date: 12/24/2016
# Name: FizzBuzz.py
# Description: A simple two-layer neural network designed to play Fizz-Buzz

import numpy as np

SIZE = 100

#Name: Sigmoid
#Desc: The Sigmoid function, used for multi-layer neural nets
#Pre: X - Value to take the sigmoid function at
#     dv - whether we're taking the derivative of the sigmopid, defaults to False
#Post: The value of the sigmoid (or derivate of sigmoid) at x
def sigmoid(x,dv=False):
    if(dv):
        return sigmoid(x)*(1-sigmoid(x))
    return 1/(1+np.exp(-x))

#Name: encodeInput
#Desc: Encodes the numerical input as a 1 x 4 Matrix, based on its value
#Pre: i - the integer input
#Post: The encoded numpy matrix
def encodeInput(i):
    if(i % 5 == 0 and i % 3 == 0):
        return np.asarray([1,0,0,0])
    if(i % 5 == 0):
        return np.asarray([0,1,0,0])
    if(i % 3 == 0):
        return np.asarray([0,0,1,0])
    return np.asarray([0,0,0,1])

#Name: makeOutput
#Desc: Creates the control values
#Pre: None
#Post: returns an NP array of dimensions SIZE x 1, with the correct values in it
def makeOutput():
    output = []
    for a in range(1, SIZE+1):
        fizz = 0
        buzz = 0
        if(a % 3 == 0):
            fizz = 0.33
        if(a % 5 == 0):
            buzz = 0.67
        output.append(fizz+buzz)
    return np.asarray([output]).T

#Name: makeInput
#Desc: encodes the every number in range 1..SIZE, and stores it in an array
#Pre: None
#Post: NP Array of dimensions 1 x SIZE
def makeInput():
    inpt = []
    for a in range(1, SIZE+1):
        inpt.append(encodeInput(a))
    return np.asarray(inpt)

def main():
    #Create the control
    output = makeOutput()

    #Initializes levels and synapses
    synapse0 = 2*np.random.random((4,SIZE))-1
    synapse1 = 2*np.random.random((SIZE,1))-1
    level0 = makeInput()

    #Running 10000 iterations
    for i in range(10000):
        #level1 = the sigmoid of the dot product of level0 and synapse0
        level1 = sigmoid(np.dot(level0,synapse0))
        #level 2 = the sigmoid of the dot product of level1 and synapse1
        level2 = sigmoid(np.dot(level1,synapse1))
        #error on level 2 = the training data - level2
        error2 = output - level2
        #the change in level 2 = error2 times the derivative of the sigmoid at l2
        delta2 = error2*sigmoid(level2,True)
        #error on level 1 = the change in level 2 dotted with the transpose of synapse1
        error1 = delta2.dot(synapse1.T)
        #change in level 1 = error1 times the derivative of the sigmoid at l1
        delta1 = error1*sigmoid(level1,True)
        #synapses are modified using the dot product of their level and the delta
        synapse1 += level1.T.dot(delta2)
        synapse0 += level0.T.dot(delta1)

    level2 = level2.tolist()
    k = 0

    #Dumps the neural network's output to a file
    with open("neuralnet.txt","w+") as myfile:
        while k < len(level2):
            i = level2[k]
            for j in i:
                if( j <= 0.01 and j >= 0):
                    myfile.write(str(k+1) + '\n')
                elif (j <= 0.34 and j >= 0.32):
                    myfile.write("Fizz\n")
                elif (j <= 0.68 and j >= 0.66):
                    myfile.write("Buzz\n")
                else:
                    myfile.write("FizzBuzz\n")
            k += 1
    #dumps the control value to a file
    with open ("control.txt","w+") as myfile:
        for j in range(1, SIZE+1):
            flag = False
            if(j % 3 == 0):
                myfile.write("Fizz")
                flag = True
            if(j % 5 == 0):
                myfile.write("Buzz")
                flag = True
            if(not flag):
                myfile.write(str(j))
            myfile.write("\n")



main()

