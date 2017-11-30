import sys

# Returns a single time from the trace.
# All *Times.pop() calls are now getTime(*Times)
def getTime(filereader):
    try:
        time = float(filereader.readline().strip())
        return time
    except ValueError:
        print "ValueError in file {}: unexpected end of file".format(filereader.name)
        sys.exit(1)

def pedSpawn(eventList, pedsInSystem, time, speed, distance, pedTimes, rp, uniformToExponential, debug):
    # A pedestrian is spawned in the system (a block away from the crosswalk)
    # Pedestrians are tracked as tupes of the form (spawn_time, speed)

    # Create the pedestrian
    ped = (time, speed)
    pedsInSystem.append(ped)

    # Create an event for the pedestrian's arrival at the crosswalk
    nextArrivalTime = time + distance/speed
    nextArrival = (nextArrivalTime, 'pedArrival', ped)
    eventList.put(nextArrival)
    if debug:
        print "Event added: pedArrival at {}".format(nextArrivalTime)

    # Create an event for the next pedestrian to be spawned
    nextSpawnTime = time + uniformToExponential(getTime(pedTimes), rp)
    nextSpawn = (nextSpawnTime, 'pedSpawn')
    eventList.put(nextSpawn)
    if debug:
        print "Event added: pedSpawn at {}".format(nextSpawnTime)

    return eventList, pedsInSystem, pedTimes

def pedArrival(time, eventList, ped, pedsInSystem, pedsWaiting, light, lastLightChange, buttonTimes, debug):
    # A pedestrian arrives at the crosswalk

    # Remove the arriving pedestrian from the system
    index = pedsInSystem.index(ped)
    ped = pedsInSystem.pop(index)
    ped += (time,)
    if debug:
        print ped

    # If the cross sign is green upon arrival
    if light == 'green':
        crosstime = 46/ped[1]       # Calculate time needed to cross

        if debug:
            print "Pedestrian speed: {}".format(ped[1])
            print "Cross time: {}".format(crosstime)
            print "Remaining time on crosswalk: {}".format(18 - time + lastLightChange)

        if crosstime < 18 - (time - lastLightChange):   # If the ped has enough time to cross
            exitTime = time + crosstime                 # Create and enqueue the event for the pedestrian leaving the system
            ped += (time,)
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
            if debug:
                print "Event added: pedExit at {}".format(exitTime)
        else:                                           # If the ped cannot cross in time
            pedsWaiting.append(ped)
    else:
        r = getTime(buttonTimes)       # If the cross sign is not green,
        n = len(pedsWaiting)        # determine if the ped will push the button
        if debug:
            print "Random number generated: {}".format(r)
            print "Target random number: {}".format(15./16 if n == 0 else 1./(n+1))
        if (n == 0 and r < (15./16)):
            eventList.put((time, 'buttonPress'))        # Push the button now
            if debug:
                print "Event added: buttonPress at {}".format(time)
        elif (n > 0 and r < (1./(n+1))):
            eventList.put((time, 'buttonPress'))        # Push the button now
            if debug:
                print "Event added: buttonPress at {}".format(time)
        else:
            eventList.put((time+60, 'pedImpatient'))    # Don't push button, make event for impatience
            if debug:
                print "Event added: pedImpatient at {}".format(time+60)
        pedsWaiting.append(ped)
        
    return pedsInSystem, pedsWaiting, eventList, buttonTimes

def pedExit(time, pedDelays, ped, debug):
    # A pedestrian exits the system
    expectedTime = (330+46*2)/ped[1]            # Calculate their optimal time to get through the system
    delay = ped[3] - ped[2]                     # Delay is however long you were at the crosswalk
    pedDelays.append(delay)                     # Add delay to list

    if debug:
        print "Pedestrian exiting."
        print "Pedestrian entered at time {0:.2f} with speed {1:.2f}".format(ped[0], ped[1])
        print "Current time: {0:.2f}".format(time)
        print "Optimal time: {0:.2f}".format(expectedTime)
        print "Delay: {0:.2f}".format(delay)
    return pedDelays

def pedImpatient(time, eventList, lastEndWalk, debug):
    # A pedestrian has become impatient

    # This if block prevents peds from getting impatient if there has been a walk sign in the last minute
    if (time - lastEndWalk) < (60 - .000001):     # Note: allowing for some small roundoff error
        return eventList

    # Push the button now
    eventList.put((time, 'buttonPress'))
    if debug:
        print "Event added: buttonPress at {}".format(time)
    return eventList

def buttonPress(time, eventList, lastLightChange, debug):
    # A pedestrian pushes a button

    # If the minimum time for a green light has been exceeded,
    # change the color of the traffic light now
    if (time - lastLightChange) > 35:
        eventList.put((time, 'greenExpires'))
        if debug:
            print "Event added: greenExpires at {}".format(time)

    # Note: If the minimum hasn't been exceeded, we don't need to make a new event
    # because there already is one
    return eventList

def autoSpawn(eventList, autosInSystem, time, speed, distance, autoTimes, ra, uniformToExponential, debug):
    # An automobile is spawned in the system
    auto = (time, speed)
    autosInSystem.append(auto)
    
    # Create an event for the auto's arrival at the crosswalk
    # May change to trigger on greenExpires
    nextArrivalTime = time + distance/speed
    nextArrival = (nextArrivalTime, 'autoArrival', auto)
    eventList.put(nextArrival)
    if debug:
        print "Event added: autoArrival at {}".format(nextArrivalTime)
    
    # Create an event for the next auto to be spawned
    nextSpawnTime = time + uniformToExponential(getTime(autoTimes), ra)
    nextSpawn = (nextSpawnTime, 'autoSpawn')
    eventList.put(nextSpawn)

    if debug:
        print "Event added: autoSpawn at {}".format(nextSpawnTime)
    return autosInSystem, autoTimes


def autoArrival(time, eventList, auto, distance, autosInSystem, autosWaiting, light, lastLightChange, debug):
    # An automobile arives at the intersection
    
    # Remove the arriving auto from the system
    index = autosInSystem.index(auto)
    auto = autosInSystem.pop(index)
    if debug:
        print auto
    
    if light == 'yellow':
        t = 33 / auto[1]                      # Time to cross
        tr = 8 - (time - lastLightChange)     # Time remaining on light

        if debug:
            print "Time remaining: {0:.2f}".format(tr)
            print "Time to cross: {0:.2f}".format(t)

        if tr > t:                            # If there's enough time to cross
            exitTime = time + distance/auto[1];      # Exit the system
            exitEvent = (exitTime, 'autoExit', auto)
            eventList.put(exitEvent)

            if debug:
                print "Event added: autoExit at time {}".format(exitTime)

        else:
            autosWaiting.append(auto)         # Just assume they knew when to break

    elif light == 'red':
        autosWaiting.append(auto)         # Just assume they knew when to break

    else:
        exitTime = time + distance/auto[1];
        exitEvent = (exitTime, 'autoExit', auto)
        eventList.put(exitEvent)
        if debug:
            print "Event added: autoExit at time {}".format(exitTime)

    return autosInSystem, autosWaiting, eventList

def autoExit(time, autoDelays, auto, debug):
    # An automobile exits the system
    expectedTime = (330*7 + 46*6)/auto[1]        # Calculate their optimal time to get through the system
    actualTime = time - auto[0]
    delay = actualTime - expectedTime
    autoDelays.append(delay)                     # Add delay to list
    if debug:
        print "Auto spawn time: {}".format(auto[0])
        print "Auto speed: {}".format(auto[1])
        print "Expected time: {}".format(expectedTime)
        print "Actual time: {}".format(actualTime)
        
    return autoDelays

def redExpires(eventList, GREEN, time, debug):
    # Light changes from red to green

    # Create and enqueue the new event
    nextGreen = (time + GREEN, 'greenExpires')
    eventList.put(nextGreen)
    if debug:
        print "Event added: greenExpires at {}".format(time + GREEN)

    # End walk
    # Create an event to end the crosswalk now
    walkEnd = (time, 'endWalk')
    eventList.put(walkEnd)
    if debug:
        print "Event added: endWalk at {}".format(time)

    startAutos = (time, 'startAutos')
    eventList.put(startAutos)
    if debug:
        print "Event added: startAutos at {}".format(time)
    return eventList

def yellowExpires(eventList, RED, time, debug):
    # Light changes from yellow to red
    # Create and enqueue the new event
    nextRed = (time+RED, 'redExpires')
    eventList.put(nextRed)
    if debug:
        print "Event added: redExpires at {}".format(time+RED)

    # Initiate start walk
    # Create an event to start the crosswalk now
    walkStart = (time, 'startWalk')
    eventList.put(walkStart)
    if debug:
        print "Event added: startWalk at {}".format(time)
    return eventList

def greenExpires(eventList, YELLOW, time, debug):
    # Light changes from green to yellow
    # Create and enqueue the new event
    nextYellow = (time+YELLOW, 'yellowExpires')
    eventList.put(nextYellow)
    if debug:
        print "Event added: yellowExpires at {}".format(time+YELLOW)

    # TODO: Add code in here for the cars?
    #autosStop = (time, 'stopAutos')
    #eventList.put(autosStop)
    #if debug:
    #    print "Event added: stopAutos at {}".format(time)
    return eventList


def startAutos(time, autosWaiting, eventList, distance, debug):
    # Stops autos in system if necessary when Yellow light is triggered.
    for auto in autosWaiting:

        accDistance = auto[1]**2/20
        accTime = auto[1]/10

        travelDistance = distance - accDistance
        travelTime = travelDistance/auto[1]
        
        exitTime = time + accTime + travelTime;      # Exit the system
        exitEvent = (exitTime, 'autoExit', auto)
        eventList.put(exitEvent)

        if debug:
            print "Event added: autoExit at {}".format(exitTime)
      
      
    return eventList, []
    
def startWalk(time, pedsWaiting, eventList, debug):
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
            ped += (time,)
            exitEvent = (exitTime, 'pedExit', ped)
            eventList.put(exitEvent)
            if debug:
                print "Event added: pedExit at {}".format(exitTime)
            pedsWaiting.pop(i)
            crossed += 1
        else:
            # Don't increase i if we remove a pedestrian from the waiting line
            i += 1
    return pedsWaiting, eventList

def endWalk(time, pedsWaiting, eventList, buttonTimes, debug):
    # Any remaining pedestrians will get impatient in one minute
    if pedsWaiting:
            eventList.put((time+60, 'pedImpatient'))
            if debug:
                print "Event added: pedImpatient at {}".format(time+60)

            # Each remaining pedestrian needs to push the button with probability 15/16
            remaining = len(pedsWaiting)
            target = 1 - (1./16) ** remaining
            r = getTime(buttonTimes)

            if debug:
                print "{} pedestrians remaining".format(remaining)
                print "Target random number: {}".format(target)
                print "Random number generated: {}".format(r)

            if r < target:
                eventList.put((time, 'buttonPress'))
                if debug:
                    print "Event added: buttonPress at {}".format(time)



    return eventList, buttonTimes












































