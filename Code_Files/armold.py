import os, sys, time, keyboard

class ArmoldBrain:
    def __init__(brain):
        brain.robot = Robot()
        brain.controller = Controller()
        brain.recordedMovements = dict()
        brain.readRecordings()
    
    def readRecordings(brain):
        recordingsPath = "//home//csse//Armold//Code_Files//Recordings//"
        recordingNames = os.listdir(recordingsPath)
        recordingNames = [rn[0:-4] for rn in recordingNames if (os.path.isfile(recordingsPath + '/' + rn)) and (rn.endswith(".txt"))]
        for rn in recordingNames:
            brain.recordedMovements[rn] = Recording(rn)
    
    def recordMovement(brain, refreshRate, duration):
        if (duration != 0):
            frame = 0.0
            while(frame < duration):
                print(".", end = "")
                sys.stdout.flush()
                frame += 1.0 / refreshRate
                time.sleep(1.0 / refreshRate)
        else:
            try:
                while True:
                    if keyboard.is_pressed("q"):
                        break
                    print(".", end = "")
                    sys.stdout.flush()
                    time.sleep(1.0 / refreshRate)
            except KeyboardInterrupt:
                pass
        print("\n\nCan you describe what you just did?\n")
        moveName = input()
        print("\nCool! Armold now knows how to " + moveName + ".")
        return
    
    def playbackMovement(brain, moveName, playbackRate):
        return

    def realtimeMovement(brain):
        return
    
    def convertToServoVals(brain, sensorVals):
        return

class Recording:
    def __init__(recording, filename):
        recording.timeline = []
        recording.filename = filename
        recording.readRecordingFromFile(recording.filename)

    def readRecordingFromFile(recording, filename):
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
    print("\nTell Armold what to do!\nCommands are: rec, play, live, and quit!\n")
    command = input()
    print("\nYou told Armold '" + command + "'")
    if(command == "rec"):
        while True:
            print("\nRate of recording? (x / sec)\n")
            try:
                rateinput = input()
                refreshRate = float(rateinput)
                if (refreshRate > 0):
                    break
                else:
                    print("\nThe rate needs to be greater than 0, try again.")
            except ValueError:
                print("\n'" + rateinput + "' isn't a number, try again.")
        while True:
            print("\nHow long should Armold watch you? (Enter '0' to do so indefinitely)\n")
            try:
                durinput = input()
                duration = float(durinput)
                if (duration >= 0):
                    break
                else:
                    print("\nThe duration can't be negative, try again.")
            except ValueError:
                print("\n'" + durinput + "' isn't a number, try again.")
        print("\n- Armold is studying your movements!\n")
        brain.recordMovement(refreshRate, duration)
    elif(command == "play"):
        while True:
            print("\nWhich movement should Armold repeat?")
            for rn in brain.recordedMovements.keys():
                print(rn)
            moveinput = input()
            if moveinput in brain.recordedMovements:
                break
            else:
                print("\n'" + moveinput + "' isn't a movement Armold has memorized, try again.")
        while True:
            print("\nRate of playback? (x / sec)\n")
            try:
                rateinput = input()
                refreshRate = float(rateinput)
                if (refreshRate > 0):
                    break
                else:
                    print("\nThe rate needs to be greater than 0, try again.")
            except ValueError:
                print("\n'" + rateinput + "' isn't a number, try again.")
        print("\n- Armold is repeating your movement!")
        brain.playbackMovement(moveinput, refreshRate)
    elif(command == "live"):
        print("\n- Armold is following movements!")
    elif(command == "quit"):
        print("\n- Armold says 'Bye!'\n")
        break
    else:
        print("\n- Armold doesn't know what '" + command + "' means...")