def pedSpawn(eventList, pedsInSystem, time, speed, distance, pedTimes, rp, uniformToExponential):
    # A pedestrian is spawned in the system (a block away from the crosswalk)
    # Pedestrians are tracked as tupes of the form (spawn_time, speed)

    # Create the pedestrian
    ped = (time, speed)
    pedsInSystem.append(ped)

    # Create an event for the pedestrian's arrival at the crosswalk
    nextArrivalTime = time + distance/speed
    nextArrival = (nextArrivalTime, 'pedArrival')
    eventList.put(nextArrival)
    print "Event added: pedArrival at {}".format(nextArrivalTime)

    # Create an event for the next pedestrian to be spawned
    nextSpawnTime = time + uniformToExponential(pedTimes.pop(), rp)
    nextSpawn = (nextSpawnTime, 'pedSpawn')
    eventList.put(nextSpawn)
    print "Event added: pedSpawn at {}".format(nextSpawnTime)

    return pedsInSystem, pedTimes

def pedArrival(time, eventList, pedsInSystem, pedsWaiting, light, lastLightChange, buttonTimes):
    # A pedestrian arrives at the crosswalk

    # Get the pedestrian at the front of the queue (the one who's been walking longest)
    # TODO: This could be a minor bug, since it's possible one ped passed another on the way to the intersection
    ped = pedsInSystem.pop(0)

    # If the cross sign is green upon arrival
    if light == 'green':
        crosstime = 46/ped[1]       # Calculate time needed to cross
        print "Pedestrian speed: {}".format(ped[1])
        print "Cross time: {}".format(crosstime)
        print "Remaining time on crosswalk: {}".format(18 - time + lastLightChange)
        if crosstime < 18 - (time - lastLightChange):   # If the ped has enough time to cross
            exitTime = time + crosstime                 # Create and enqueue the event for the pedestrian leaving the system
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
            print "Event added: pedExit at {}".format(exitTime)
        else:                                           # If the ped cannot cross in time
            pedsWaiting.append(ped)                     # Create and enqueue the event for the pedestrian getting impatient
            eventList.put((time+60, 'pedImpatient'))
            print "Event added: pedImpatient at {}".format(time+60)
    else:
        r = buttonTimes.pop()       # If the cross sign is not green,
        n = len(pedsWaiting)        # determine if the ped will push the button
        print "Random number generated: {}".format(r)
        print "Target random number: {}".format(15./16 if n == 0 else 1./(n+1))
        if (n == 0 and r < (15./16)):
            eventList.put((time, 'buttonPress'))        # Push the button now
            print "Event added: buttonPress at {}".format(time)
        elif (n > 0 and r < (1./(n+1))):
            eventList.put((time, 'buttonPress'))        # Push the button now
            print "Event added: buttonPress at {}".format(time)
        else:
            eventList.put((time+60, 'pedImpatient'))    # Don't push button, make event for impatience
            print "Event added: pedImpatient at {}".format(time+60)
        pedsWaiting.append(ped)
        
    return pedsInSystem, pedsWaiting, eventList, buttonTimes

def pedExit(time, pedDelays, ped):
    # A pedestrian exits the system
    expectedTime = (330+46*2)/ped[1]            # Calculate their optimal time to get through the system
    delay = (time - ped[0]) - expectedTime      # Calculate delay
    pedDelays.append(delay)                     # Add delay to list
    return pedDelays

def pedImpatient(time, eventList, lastStartWalk):
    # A pedestrian has become impatient

    # This if block prevents peds from getting impatient if there has been a nowalk->walk transition in the last minute
    if (time - lastStartWalk) < 60:
        return eventList

    # Push the button now
    eventList.put((time, 'buttonPress'))
    print "Event added: buttonPress at {}".format(time)
    return eventList

def buttonPress(time, eventList, lastLightChange):
    # A pedestrian pushes a button

    # If the minimum time for a green light has been exceeded,
    # change the color of the traffic light now
    if (time - lastLightChange) > 35:
        eventList.put((time, 'greenExpires'))
        print "Event added: greenExpires at {}".format(time)

    # Note: If the minimum hasn't been exceeded, we don't need to make a new event
    # because there already is one
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

    # Create and enqueue the new event
    nextGreen = (time + GREEN, 'greenExpires')
    eventList.put(nextGreen)
    print "Event added: greenExpires at {}".format(time + GREEN)

    # End walk
    # Create an event to end the crosswalk now
    walkEnd = (time, 'endWalk')
    eventList.put(walkEnd)
    print "Event added: endWalk at {}".format(time)
    return eventList

def yellowExpires(eventList, RED, time):
    # Light changes from yellow to red
    # Create and enqueue the new event
    nextRed = (time+RED, 'redExpires')
    eventList.put(nextRed)
    print "Event added: redExpires at {}".format(time+RED)

    # Initiate start walk
    # Create an event to start the crosswalk now
    walkStart = (time, 'startWalk')
    eventList.put(walkStart)
    print "Event added: startWalk at {}".format(time)
    return eventList

def greenExpires(eventList, YELLOW, time):
    # Light changes from green to yellow
    # Create and enqueue the new event
    nextYellow = (time+YELLOW, 'yellowExpires')
    eventList.put(nextYellow)
    print "Event added: yellowExpires at {}".format(time+YELLOW)

    # TODO: Add code in here for the cars?
    return eventList

def startWalk(time, pedsWaiting, eventList):
    # Crosswalk sign turns on, peds start to cross
    crossed = 0
    i = 0

    # Find the first 20 pedestrians who can cross in time
    while i < len(pedsWaiting) and crossed < 20:
        ped = pedsWaiting[i]
        crosstime = 46/ped[1]
        if crosstime < 18:      # Check if the current pedestrian can cross in time
            # Create and enqueue the event to leave the system
            exitTime = time + crosstime
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
            print "Event added: pedExit at {}".format(exitTime)
            pedsWaiting.pop(i)
            crossed += 1
        else:
            # Don't increase i if we remove a pedestrian from the waiting line
            i += 1
    return pedsWaiting, eventList

def endWalk(time, pedsWaiting, eventList, buttonTimes):
    # Each remaining pedestrian needs to push the button with probability 15/16
    for ped in pedsWaiting:
        r = buttonTimes.pop()
        if r < (15./16):
            eventList.put((time, 'buttonPress'))
            print "Event added: buttonPress at {}".format(time)
    return eventList, buttonTimes












































