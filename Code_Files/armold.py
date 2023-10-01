import os, sys, time, keyboard, json

class ArmoldBrain:
    def __init__(brain):
        brain.robot = Robot()
        brain.controller = Controller()
        brain.recordedMovements = dict()
        brain.readRecordings()
    
    def readRecordings(brain):
        recordingsPath = "//Armold//Code_Files//Recordings//"
        recordingNames = os.listdir(recordingsPath)
        recordingNames = [rn[0:-4] for rn in recordingNames if (os.path.isfile(recordingsPath + '/' + rn)) and (rn.endswith(".txt"))]
        for rn in recordingNames:
            brain.recordedMovements[rn] = Recording(rn)
    
    def recordMovement(brain, refreshRate, duration):
        moveTimeline = []
        frame = 0
        secDone = 0
        if (duration == 0):
            print("  (Press Q or Ctrl+C to stop)")
        print()
        try:
            while((duration == 0) or (frame < refreshRate * duration)):
                moveTimeline.append(brain.convertToServoVals(brain.controller.getSensors()))
                if keyboard.is_pressed("q"):
                    break
                if (secDone == refreshRate):
                    print("\n")
                    secDone = 0
                print(".", end = "")
                sys.stdout.flush()
                frame += 1
                secDone += 1
                time.sleep(1.0 / refreshRate)
        except KeyboardInterrupt:
            pass
        print(f"\n\n{frame} frames memorized.")
        print("\nCan you describe what you just did?\n")
        moveName = input("> ")
        recordingsPath = "//Armold//Code_Files//Recordings//"
        moveFullPath = os.path.join(recordingsPath, moveName + ".txt")
        moveFile = open(moveFullPath, "w")
        moveFile.write(f"{refreshRate}")
        for frameData in moveTimeline:
            moveFile.write(f"\n{frameData}")
        moveFile.close()
        newRecording = Recording(moveName)
        newRecording.timeline = moveTimeline
        brain.recordedMovements[moveName] = newRecording
        print("\nCool! Armold now knows how to " + moveName + ".")
        return
    
    def playbackMovement(brain, moveName, playbackRate):
        print("  (Press Q or Ctrl+C to stop)")
        print()
        frame = 0
        secDone = 0
        movement = brain.recordedMovements[moveName]
        recLen = round(len(movement.timeline) * (1.0 / playbackRate), 2)
        try:
            while(frame < len(movement.timeline)):
                if keyboard.is_pressed("q"):
                    break
                if (frame % playbackRate == 0):
                    print(f"{recLen - secDone} seconds left...")
                    secDone += 1
                brain.robot.setServos(brain.convertToServoVals(movement.getServosAtTime(frame)))
                frame += 1
                time.sleep(1.0 / refreshRate)
        except KeyboardInterrupt:
            pass
        print(f"\nArmold is done performing '{moveName}!'")
        return

    def realtimeMovement(brain, refreshRate):
        print("  (Press Q or Ctrl+C to stop)")
        print()
        try:
            while(True):
                if keyboard.is_pressed("q"):
                    break
                brain.robot.setServos(brain.convertToServoVals(brain.controller.getSensors()))
                time.sleep(1.0 / refreshRate)
        except KeyboardInterrupt:
            pass
        return
    
    def convertToServoVals(brain, sensorVals):
        servoVals = dict()
        return servoVals

class Recording:
    def __init__(recording, filename):
        recording.filename = filename
        recording.originalRate = 1
        recording.timeline = []
        recording.readRecordingFromFile(recording.filename)

    def readRecordingFromFile(recording, filename):
        recordingsPath = "//Armold//Code_Files//Recordings//"
        moveFullPath = os.path.join(recordingsPath, recording.filename + ".txt")
        moveFile = open(moveFullPath, "r")
        try:
            rateVal = moveFile.readline()
            recording.originalRate = float(rateVal)
            for frame in moveFile:
                recording.timeline.append(json.loads(frame))
            print(recording.timeline)
        except ValueError:
            recording.originalRate = 1
            print("badval")
        moveFile.close()
        return
    
    def getServosAtTime(recording, time):
        return recording.timeline[time]

class Robot:
    def __init__(robot):
        robot.servos = dict()
        robot.createServoConnections()
    
    def createServoConnections(robot):
        return

    def setServos(robot, newVals):
        return

class Controller:
    def __init__(controller):
        controller.sensors = dict()
        controller.createSensorConnections()
    
    def createSensorConnections(controller):
        return

    def getSensors(controller):
        return

# main loop
brain = ArmoldBrain()
while True:
    time.sleep(0.25)
    print("\nTell Armold what to do!",
            "\nCommands are:",
            "\n- (s) study movement",
            "\n- (p) perform movement",
            "\n- (l) mirror live movement",
            "\n- (m) move servo",
            "\n- (q) quit\n")
    command = input("> ")
    if(command == "s"):
        print("\nYou told Armold to study your movements.")
        while True:
            print("\nRate of recording? (Hz)\n")
            try:
                rateinput = input("> ")
                refreshRate = float(rateinput)
                if (refreshRate > 1):
                    break
                else:
                    print("\nThe rate needs to be greater than 1, try again.")
            except ValueError:
                print("\n'" + rateinput + "' isn't a number, try again.")
        while True:
            print("\nHow many seconds should Armold watch you? (Enter '0' to do so indefinitely)\n")
            try:
                durinput = input("> ")
                duration = float(durinput)
                if (duration >= 0):
                    break
                else:
                    print("\nThe duration can't be negative, try again.")
            except ValueError:
                print("\n'" + durinput + "' isn't a number, try again.")
        print("\n- Armold is studying your movements!")
        brain.recordMovement(refreshRate, duration)
    elif(command == "p"):
        print("\nYou told Armold to perform a movement.")
        while True:
            print("\nWhich movement should Armold repeat?")
            for rn, rec in brain.recordedMovements.items():
                print(f"- {rn} ({len(rec.timeline)} frames, {round(len(rec.timeline) * (1.0 / rec.originalRate), 2)} secs at {rec.originalRate} Hz originally)")
            print()
            moveinput = input("> ")
            if moveinput in brain.recordedMovements:
                break
            else:
                print("\n'" + moveinput + "' isn't a movement Armold has memorized, try again.")
        while True:
            print("\nRate of playback? (Hz)\n")
            try:
                rateinput = input("> ")
                refreshRate = float(rateinput)
                if (refreshRate >= 1):
                    break
                else:
                    print("\nThe rate needs to be at least 1.0, try again.")
            except ValueError:
                print("\n'" + rateinput + "' isn't a number, try again.")
        print("\n- Armold is going to " + moveinput + "!")
        brain.playbackMovement(moveinput, refreshRate)
    elif(command == "l"):
        print("\nYou told Armold to mirror your movements in real-time.")
        while True:
            print("\nRate of recording? (Hz)\n")
            try:
                rateinput = input("> ")
                refreshRate = float(rateinput)
                if (refreshRate > 1):
                    print("\n- Armold is mirroring your movements!")
                    brain.realtimeMovement(refreshRate)
                    break
                else:
                    print("\nThe rate needs to be greater than 1, try again.")
            except ValueError:
                print("\n'" + rateinput + "' isn't a number, try again.")
    elif(command == "m"):
        print("\nYou told Armold to move a servo.")
        print("\nWhich pin is the servo on?")
        pininput = input("> ")
        print("\nWhat value should the pin be given?")
        valinput = input("> ")
    elif(command == "q"):
        print("\n- Armold says 'Bye!'\n")
        break
    else:
        print("\n- Armold doesn't know what '" + command + "' means...")