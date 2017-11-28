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
lastEndWalk = 0
buttonPressed = True
spawnCount = 0
pedsExited = 0



# If you want detailed outputs to the screen, set this to true
# Note that it pauses after each event, so leave false when running grader script
# Press enter to continue through pause
debug = True


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
    # Needs to be cast to an int for the grader script
    N = int(N)

    # Globalizing things
    # If you get an error that says "Using variable before declared", add it to this list
    global time
    global eventList
    global autoTimes
    global pedTimes
    global buttonTimes
    global spawnCount
    global debug


    # Create file readers for uniform distributions
    autoTimes = initializeReader(randomAuto)
    pedTimes = initializeReader(randomPed)
    buttonTimes = initializeReader(randomButtons)

    # Define system state variables
    eventCounter = 0;

    # Define initial event times
    nextPedTime = time + uniformToExponential(getTime(pedTimes), rp)
    nextAutoTime = time + uniformToExponential(getTime(autoTimes), ra)
    nextLightChange = time
    nextButtonPress = time

    # Define initial events
    nextPed = (nextPedTime, 'pedSpawn')
    nextAuto = (nextAutoTime, 'autoSpawn')
    nextLight = (nextLightChange, 'greenExpires')
    nextButton = (nextButtonPress, 'buttonPress')

    # Enqueue initial events
    eventList.put(nextPed)
    eventList.put(nextAuto)
    eventList.put(nextLight)

    # Continue unti we've spawned the specified number of autos and peds
    while (spawnCount < N):

        # Get the next event
        event = eventList.get()
        time = event[0]
        if debug:       # Detailed output
            print "~~~~~~~~~~Next event~~~~~~~~~~"
            print "Event type: {}".format(event[1])
            print "Events to date: {}".format(eventCounter)
            print "Spawns to date: {}".format(spawnCount)
            print "Time: {}".format(event[0])
            print "Last crosswalk ended at: {}".format(lastEndWalk)
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

            
        # Process the next event
        processEvent(event, N)
        eventCounter += 1

        # Pause if debugging
        if debug:
            print
            raw_input()
            
        # If we've run out of events for some reason, break
        # Note that we should never get to this point
        if (eventList.empty()):
            break

    # Output for grader script
    print "OUTPUT {} {} {}".format(0,0, np.mean(pedDelays))



def uniformToExponential(u, l):     # u is uniform, l is associated lambda
    e = -math.log(u)/l              # called l because lambda is reseved in python
    return e

# Open file reader with given filename. Nonzero exit if IOError occurs.
def initializeReader(filename):
    try:
        reader = open(filename, 'r')
        print "Successfully opened {}".format(filename)
        return reader
    except IOError:
        print "Error opening file {}: no such file or directory".format(filename)
        sys.exit(1)

# Returns a single time from the trace.
# All *Times.pop() calls are now getTime(*Times)
def getTime(filereader):
    try:
        time = float(filereader.readline().strip())
        return time
    except ValueError:
        print "ValueError in file {}: unexpected end of file".format(filereader.name)
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
    global autosInSystem, autosWaiting, autoDelays, autoTimes
    global walkLight, lastLightChange, driveLight
    global buttonPressed, buttonTimes
    global lastEndWalk
    global debug

    e = event[1]
    
    if (e == 'pedSpawn'):
        spawnCount += 1
        speed = getTime(pedTimes)*(4.1-2.6) + 2.6
        if debug:
            print "Pedestrian spawned at time {0:.2f} with speed {1:.2f}".format(time, speed)
        eventList, pedsInSystem, pedTimes= pedSpawn(eventList, pedsInSystem, time, \
                    speed, B + S, \
                    pedTimes, rp, uniformToExponential, debug)

        
    elif (e == 'pedArrival'):
        ped = event[2]
        pedsInSystem, pedsWaiting, eventList, buttonTimes = \
                      pedArrival(time, eventList, ped, pedsInSystem, pedsWaiting, \
                      walkLight, lastLightChange, buttonTimes, debug)
        
    elif (e == 'pedExit'):
        ped = event[2]
        pedDelays = pedExit(time, pedDelays, ped, debug)

    elif (e == 'pedImpatient'):
        eventList = pedImpatient(time, eventList, lastEndWalk, debug)
        
    elif (e == 'buttonPress'):
        buttonPressed = True
        eventList = buttonPress(time, eventList, lastLightChange, debug)
        
    elif (e == 'autoSpawn'):
        N += 1
        speed = (getTime(autoTimes)*(35.0-25.0) + 25.0)/3600 * 5280  # Feet per second
        if debug:
            print "Auto spawned at time {0:.2f} with speed {1:.2f}".format(time,speed)
        autosInSystem, autoTimes = autoSpawn(eventList, autosInSystem, time, speed, \
                      B*3.5 + 3*S - 12, autoTimes, ra, uniformToExponential, debug) 
                      # B*3.5 + 3*S - 12 = distance to edge of crosswalk; 3.5 blocks, 3 streets, minus half crosswalk width
                      # ToDo: Check whether the back of the car has crossed over the crosswalk at greenExpires
        
    elif (e == 'autoArrival'):
        auto = event[2]
        autosInSystem, autosWaiting, eventList = autoArrival(time, eventList, auto, \
                      autosInSystem, autosWaiting, walkLight, lastLightChange, debug)
        
    elif (e == 'autoExit'):
        autoExit()
        
    elif (e == 'redExpires'):
        lastLightChange = time
        driveLight = 'green'
        eventList = redExpires(eventList, GREEN, time, debug)
        
    elif (e == 'yellowExpires'):
        lastLightChange = time
        driveLight = 'red'
        eventList = yellowExpires(eventList, RED, time, debug)
        
    elif (e == 'greenExpires'):
        if buttonPressed:
            lastLightChange = time
            driveLight = 'yellow'
            eventList = greenExpires(eventList, YELLOW, time, debug)
            
    elif (e == 'stopAutos'):
        eventList, autosWaiting, autosInSystem = stopAutos(time, autosWaiting, autosInSystem, \
                      eventList, B*3.5 + S*3 - 12, debug)
        
    elif (e == 'startWalk'):
        walkLight = 'green'
        pedsWaiting, eventList = startWalk(time, pedsWaiting, eventList, debug)
        
    elif (e == 'endWalk'):
        walkLight = 'red'
        lastEndWalk = time
        buttonPressed = False
        eventList, buttonTimes = endWalk(time, pedsWaiting, eventList, buttonTimes, debug)
        
    return






























































    
if __name__ == '__main__':
    main(400, 'uniform-0-1-00.dat', 'uniform-0-1-05.dat', 'uniform-0-1-02.dat')
