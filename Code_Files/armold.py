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
        frame = 0
        secDone = 0
        if (duration != 0):
            print()
            while(frame < refreshRate * duration):
                if (secDone == refreshRate):
                    print("\n")
                    secDone = 0
                frame += 1
                secDone += 1
                print(".", end = "")
                sys.stdout.flush()
                time.sleep(1.0 / refreshRate)
        else:
            print("  (Press Q or Ctrl+C to stop)\n")
            try:
                while True:
                    if keyboard.is_pressed("q"):
                        break
                    if (secDone == refreshRate):
                        print("\n")
                        secDone = 0
                    frame += 1
                    secDone += 1
                    print(".", end = "")
                    sys.stdout.flush()
                    time.sleep(1.0 / refreshRate)
            except KeyboardInterrupt:
                pass
        print(f"\n\n{frame} frames memorized.")
        print("\nCan you describe what you just did?\n")
        moveName = input("> ")
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
        recording.originalRate = 1
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
                print(f"- {rn} ({len(rec.timeline)} frames, {len(rec.timeline) * (1.0 / rec.originalRate)} secs at {rec.originalRate} Hz originally)")
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
                if (refreshRate > 1):
                    break
                else:
                    print("\nThe rate needs to be greater than 1, try again.")
            except ValueError:
                print("\n'" + rateinput + "' isn't a number, try again.")
        print("\n- Armold is going to " + moveinput + "!")
        brain.playbackMovement(moveinput, refreshRate)
    elif(command == "l"):
        print("\nYou told Armold to mirror your movements in real-time.")
        print("\n- Armold is mirroring your movements!")
    elif(command == "m"):
        print("\nYou told Armold to move a servo.")
        print("\n- Okay.")
    elif(command == "q"):
        print("\n- Armold says 'Bye!'\n")
        break
    else:
        print("\n- Armold doesn't know what '" + command + "' means...")