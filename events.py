def pedSpawn(eventList, pedsInSystem, time, speed, distance, pedTimes, rp, uniformToExponential):
    # A pedestrian is spawned in the system (a block away from the crosswalk)
    ped = (time, speed)
    pedsInSystem.append(ped)

    nextArrivalTime = time + distance/speed
    nextArrival = (nextArrivalTime, 'pedArrival')
    eventList.put(nextArrival)
    print "Event added: pedArrival at {}".format(nextArrivalTime)

    nextSpawnTime = time + uniformToExponential(pedTimes.pop(), rp)
    nextSpawn = (nextSpawnTime, 'pedSpawn')
    eventList.put(nextSpawn)
    print "Event added: pedSpawn at {}".format(nextSpawnTime)

    
    return pedsInSystem, pedTimes

def pedArrival(time, eventList, pedsInSystem, pedsWaiting, light, lastLightChange, buttonTimes):
    # A pedestrian arrives at the crosswalk
    ped = pedsInSystem.pop(0)
    if light == 'green':
        crosstime = 46/ped[1]
        if crosstime < 18 - (time - lastLightChange):
            exitTime = time + crosstime
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
            print "Event added: pedExit at {}".format(exitTime)
        else:
            pedsWaiting.append(ped)
            eventList.put((time+60, 'pedImpatient'))
            print "Event added: pedImpatient at {}".format(time+60)
    else:
        pedsWaiting.append(ped)
        r = buttonTimes.pop()
        n = len(pedsWaiting)
        if (n == 0 and r < (15./16)):
            eventList.put((time, 'buttonPress'))
            print "Event added: buttonPress at {}".format(time)
        elif (n > 0 and r < (1./(n+1))):
            eventList.put((time, 'buttonPress'))
            print "Event added: buttonPress at {}".format(time)
        else:
            eventList.put((time+60, 'pedImpatient'))
            print "Event added: pedImpatient at {}".format(time+60)
        
    return pedsInSystem, pedsWaiting, eventList, buttonTimes

def pedExit(time, pedDelays, ped):
    # A pedestrian exits the system
    expectedTime = (330+46*2)/ped[1]
    delay = (time - ped[0]) - expectedTime
    pedDelays.append(delay)
    return pedDelays

def pedImpatient(time, eventList, lastStartWalk):
    # A pedestrian has become impatient
    if (time - lastStartWalk) < 60:
        return
    eventList.put((time, 'buttonPress'))
    print "Event added: buttonPress at {}".format(time)
    return

def buttonPress(time, eventList, lastLightChange):
    # A pedestrian pushes a button
    if (time - lastLightChange) > 35:
        eventList.put((time, 'greenExpires'))
        print "Event added: greenExpires at {}".format(time)
    return eventList

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
    nextGreen = (time + GREEN, 'greenExpires')
    eventList.put(nextGreen)
    print "Event added: greenExpires at {}".format(time + GREEN)

    # End walk
    walkEnd = (time, 'endWalk')
    eventList.put(walkEnd)
    print "Event added: endWalk at {}".format(time)
    return eventList

def yellowExpires(eventList, RED, time):
    # Light changes from yellow to red
    nextRed = (time+RED, 'redExpires')
    eventList.put(nextRed)
    print "Event added: redExpires at {}".format(time+RED)

    # Initiate start walk
    walkStart = (time, 'startWalk')
    eventList.put(walkStart)
    print "Event added: startWalk at {}".format(time)
    return eventList

def greenExpires(eventList, YELLOW, time):
    # Light changes from green to yellow
    nextYellow = (time+YELLOW, 'yellowExpires')
    eventList.put(nextYellow)
    print "Event added: yellowExpires at {}".format(time+YELLOW)
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
            print "Event added: pedExit at {}".format(exitTime)
            pedsWaiting.pop(i)
            crossed += 1
        else:
            i += 1
    return pedsWaiting, eventList














































