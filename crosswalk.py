from events import *
import Queue as Q
import math

# Defining some global variables
# This is to prevent function calls with a million parameters and return values
pedDelays = []
autoDelays = []
pedsInSystem = []       # Needs to be treated as a queue, but also needs to have indexed-based access
autosInSystem = []      # See above comment
autoTimes = []
pedTimes = []
buttonTimes = []
eventList = Q.PriorityQueue()
time = 0.   # Global system time

def uniformToExponential(u, l):     # u is uniform, l is associated lambda
    e = -math.log(u)/l              # called l because lambda is reseved in python
    return e

def getTimes(filename):
    times = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            times.append(float(line.strip()))
    return times

def processEvent(e):
    # This is going to be where the bulk of the work is contained.
    # I'm thinking we have this check what type of event e is
    # and call the associated function for proccessing that
    # particular event.
    # For clarity sake, I have defined these helper
    # functions in a separate file
    
    if (e == 'pedSpawn'):
        pedSpawn()
    elif (e == 'pedArrival'):
        pedArrival()
    elif (e == 'pedExit'):
        pedExit()
    elif (e == 'buttonPress'):
        buttonPress()
    elif (e == 'autoSpawn'):
        autoSpawn()
    elif (e == 'autoArrival'):
        autoArrival()
    elif (e == 'autoExit'):
        autoExit()
    elif (e == 'redExpires'):
        redExpires()
    elif (e == 'yellowExpires'):
        yellowExpires()
    elif (e == 'greenExpires'):
        greenExpires()
    elif (e == 'startWalk'):
        startWalk()
    elif (e == 'endWalk'):
        endWalk()
    return

def main(N, randomAuto, randomPed, randomButtons):
    B = 330     # Width of a residential block
    w = 24      # Width of crosswalk
    S = 46      # Width of street 
    RED = 18    # Time traffic signal is red
    YELLOW = 8  # Time traffic signal is yellow
    GREEN = 35  # Minimum time traffic signal is green
    rp = 3      # Arrival rate of pedestrians (per minute)
    ra = 4      # Arrival rate of automobiles (per minute)
    L = 9       # Length of an automobile
                # vj: auto speed, Uniform(25,35) mph
                # a: auto acceleration, 10 ft/s/s
                # vk: ped speek, uniform(2.6, 4.1) ft/s

    # Create arrays of uniform distributions
    autoTimes = getTimes(randomAuto)
    pedTimes = getTimes(randomPed)
    buttonTimes = getTimes(randomButtons)

    # Define system state variables
    light = 'g'
    eventCounter = 0;

    # Define initial event times
    nextPedTime = time + uniformToExponential(pedTimes.pop(), rp)
    nextAutoTime = time + uniformToExponential(autoTimes.pop(), ra)
    nextLightChange = time
    nextButtonPress = time

    # Define initial events
    nextPed = (nextPedTime, 'pedArrival')
    nextAuto = (nextAutoTime, 'autoArrival')
    nextLight = (nextLightChange, 'greenExpires')
    nextButton = (nextButtonPress, 'buttonPress')

    # Enqueue initial events
    # TODO: Uncomment when it's time to work on peds
    #eventList.put(nextPed)
    # TODO: Uncomment when it's time to work on autos
    #eventList.put(nextAuto)
    eventList.put(nextLight)
    # TODO: Unocmment when it's time to work on autos
    #eventList.put(nextButton)

    while (eventCounter < N):
        e = eventList.get()
        print e
        processEvent(e)
        eventCounter += 1
        raw_input()
        break


































































    
if __name__ == '__main__':
    main(100, 'uniform-0-1-00.dat', 'uniform-0-1-01.dat', 'uniform-0-1-02.dat')
