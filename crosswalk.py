from events import *
import Queue as Q
import math, numpy as np
import sys

# Defining some global system variables
# This is to prevent function calls with a million parameters and return values
time = 0
buttonTimes = []
pedTimes = []
autoTimes = []
autosInSystem = []          # Needs to be treated as a queue, but also needs to have indexed-based access
pedsInSystem = []           # See above comment
pedsWaiting = []
autosWaiting = []
autoDelays = []
pedDelays = []
eventList = Q.PriorityQueue()
walkLight = 'red'
driveLight = 'green'
lastLightChange = 0
lastStartWalk = 0
buttonPressed = True
spawnCount = 0


# Defining some global constants
B = 330     # Width of a residential block
w = 24      # Width of crosswalk
S = 46      # Width of street 
RED = 18    # Time traffic signal is red
YELLOW = 8  # Time traffic signal is yellow
GREEN = 35  # Minimum time traffic signal is green
rp = 3./60   # Arrival rate of pedestrians (per second)
ra = 4./60   # Arrival rate of automobiles (per second)
L = 9       # Length of an automobile
            # vj: auto speed, Uniform(25,35) mph = Uniform(25,35)/360 miles/second
            # a: auto acceleration, 10 ft/s/s
            # vk: ped speek, uniform(2.6, 4.1) ft/s

def main(N, randomAuto, randomPed, randomButtons):
    N = int(N)

    print N, randomAuto, randomPed, randomButtons
    return
    
    global time
    global eventList
    global autoTimes
    global pedTimes
    global buttonTimes
    global spawnCount

    debug = False

    # Create arrays of uniform distributions
    autoTimes = getTimes(randomAuto)
    pedTimes = getTimes(randomPed)
    buttonTimes = getTimes(randomButtons)

    # Define system state variables
    eventCounter = 0;

    # Define initial event times
    nextPedTime = time + uniformToExponential(pedTimes.pop(), rp)
    nextAutoTime = time + uniformToExponential(autoTimes.pop(), ra)
    nextLightChange = time
    nextButtonPress = time

    # Define initial events
    nextPed = (nextPedTime, 'pedSpawn')
    nextAuto = (nextAutoTime, 'autoSpawn')
    nextLight = (nextLightChange, 'greenExpires')
    nextButton = (nextButtonPress, 'buttonPress')

    # Enqueue initial events
    eventList.put(nextPed)
    #eventList.put(nextAuto)
    eventList.put(nextLight)
    #eventList.put(nextButton)
    #eventList.put((120, 'startWalk'))

    while (spawnCount < N):
        event = eventList.get()
        time = event[0]
        if debug:
            print "~~~~~~~~~~Next event~~~~~~~~~~"
            print "Event type: {}".format(event[1])
            print "Events to date: {}".format(eventCounter)
            print "Spawns to date: {}".format(spawnCount)
            print "Time: {}".format(event[0])
            print "Last crosswalk started at: {}".format(lastStartWalk)
            print "Last light change at: {}".format(lastLightChange)
            print "Stoplight color: {}".format(driveLight)
            print "Crosswalk color: {}".format(walkLight)
            print "Button pressed: {}".format(buttonPressed)
            print "Number of pedestrains in system: {}".format(len(pedsInSystem))
            print "Number of pedestrains waiting: {}".format(len(pedsWaiting))
            print "Number of pedestrains crossed: {}".format(len(pedDelays))
            print "Number of automobiles in system: {}".format(len(autosInSystem))
            print "Number of automobiles waiting: {}".format(len(autosWaiting))
            print "Number of automobiles crossed: {}".format(len(autoDelays))

            
        
        processEvent(event, N)
        eventCounter += 1
        if debug:
            print
            raw_input()

        if (eventList.empty()):
            break
    
    print "OUTPUT {} {} {}".format(0,0, np.mean(pedDelays))



def uniformToExponential(u, l):     # u is uniform, l is associated lambda
    e = -math.log(u)/l              # called l because lambda is reseved in python
    return e

def getTimes(filename):
    try:
        times = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                times.append(float(line.strip()))
        return times
    except IOError:
        print "Error opening file {}: no such file or directory".format(filename)
        sys.exit(1)

def processEvent(event, N):
    # This is going to be where the bulk of the work is contained.
    # I'm thinking we have this check what type of event e is
    # and call the associated function for proccessing that
    # particular event.
    # For clarity sake, I have defined these helper
    # functions in a separate file

    # Because python is weird, need to specify that eventList is global
    global eventList, spawnCount
    global pedsInSystem, pedsWaiting, pedDelays, pedTimes
    global autosInSystem, autosWaiting, autoDelays
    global walkLight, lastLightChange, driveLight
    global buttonPressed, buttonTimes
    global lastStartWalk

    e = event[1]
    
    if (e == 'pedSpawn'):
        spawnCount += 1
        speed = pedTimes.pop()*(4.1-2.6) + 2.6
        print "Pedestrian spawned at time {0:.2f} with speed {1:.2f}".format(time, speed)
        pedsInSystem, pedTimes = pedSpawn(eventList, pedsInSystem, time, speed, B + S, pedTimes, rp, uniformToExponential)
        
    elif (e == 'pedArrival'):
        pedsInSystem, pedsWaiting, eventList, buttonTimes = \
                      pedArrival(time, eventList, pedsInSystem, pedsWaiting, walkLight, lastLightChange, buttonTimes)
        
    elif (e == 'pedExit'):
        ped = event[2]
        pedDelays = pedExit(time, pedDelays, ped)

    elif (e == 'pedImpatient'):
        pedImpatient(time, eventList, lastStartWalk)
        
    elif (e == 'buttonPress'):
        buttonPressed = True
        eventList = buttonPress(time, eventList, lastLightChange)
        
    elif (e == 'autoSpawn'):
        N += 1
        autosInSystem = autoSpawn(autosInSystem, time)
        
    elif (e == 'autoArrival'):
        autoArrival()
        
    elif (e == 'autoExit'):
        autoExit()
        
    elif (e == 'redExpires'):
        lastLightChange = time
        driveLight = 'green'
        eventList = redExpires(eventList, GREEN, time)
        
    elif (e == 'yellowExpires'):
        lastLightChange = time
        driveLight = 'red'
        eventList = yellowExpires(eventList, RED, time)
        
    elif (e == 'greenExpires'):
        if buttonPressed:
            lastLightChange = time
            driveLight = 'yellow'
            eventList = greenExpires(eventList, YELLOW, time)
        
    elif (e == 'startWalk'):
        walkLight = 'green'
        lastStartWalk = time
        pedsWaiting, eventList = startWalk(time, pedsWaiting, eventList)
        
    elif (e == 'endWalk'):
        walkLight = 'red'
        buttonPressed = False
        
    return






























































    
if __name__ == '__main__':
    main(200, 'uniform-0-1-00.dat', 'uniform-0-1-03.dat', 'uniform-0-1-02.dat')
