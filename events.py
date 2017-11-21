def pedSpawn(eventList, pedsInSystem, time, speed, distance):
    # A pedestrian is spawned in the system (a block away from the crosswalk)
    # TODO: Add ped to system
    ped = (time, speed)
    pedsInSystem.append(ped)

    nextArrivalTime = distance/speed
    nextArrival = (time + nextArrivalTime, 'pedArrival')
    eventList.put(nextArrival)
    return pedsInSystem

def pedArrival(time, eventList, pedsInSystem, pedsWaiting, light, lastLightChange):
    # A pedestrian arrives at the crosswalk
    ped = pedsInSystem.pop(0)
    if light == 'green':
        crosstime = 46/ped[1]
        if crosstime < 18 - (time - lastLightChange):
            exitTime = time + crosstime
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
    else:
        pedsWaiting.append(ped)
        
    return pedsInSystem, pedsWaiting, eventList

def pedExit(time, pedDelays, ped):
    # A pedestrian exits the system
    expectedTime = (330+46*2)/ped[1]
    delay = (time - ped[0]) - expectedTime
    pedDelays.append(delay)
    return pedDelays

def buttonPress():
    # A pedestrian pushes a button
    return

def autoSpawn(eventList, autosInSystem, autoTimes, time):
    # An automobile is spawned in the system
    #TODO: Add auto to system
    autosInSystem.append(time)
    return

def autoArrival():
    # An automobile arives at the intersection
    return

def autoExit():
    # An automobile exits the system
    return

def redExpires(eventList, GREEN, time):
    # Light changes from red to green

    # TODO: Calculate how long light will be green
    
    nextGreen = (time + GREEN, 'greenExpires')
    eventList.put(nextGreen)

    # End walk
    walkEnd = (time, 'endWalk')
    eventList.put(walkEnd)
    return eventList

def yellowExpires(eventList, RED, time):
    # Light changes from yellow to red
    nextRed = (time+RED, 'redExpires')
    eventList.put(nextRed)

    # Initiate start walk
    walkStart = (time, 'startWalk')
    eventList.put(walkStart)
    return eventList

def greenExpires(eventList, YELLOW, time):
    # Light changes from green to yellow
    nextYellow = (time+YELLOW, 'yellowExpires')
    eventList.put(nextYellow)
    return eventList

def startWalk(time, pedsWaiting, eventList):
    # Crosswalk sign turns on, peds start to cross
    crossed = 0
    i = 0
    while i < len(pedsWaiting) and crossed < 20:
        ped = pedsWaiting[i]
        crosstime = 46/ped[1]
        if crosstime < 18:
            exitTime = time + crosstime
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
            pedsWaiting.pop(i)
            crossed += 1
        else:
            i += 1
    return pedsWaiting, eventList

def endWalk(pedsInSystem):
    # Crosswalk sign turns off, no more crossing
    return














































