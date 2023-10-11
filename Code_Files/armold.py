import os, sys, time, keyboard, json
import RPi.GPIO as GPIO
import gpiozero
import pigpio

class ArmoldBrain:
    # initialization
    def __init__(brain):
        brain.robot = Robot()
        brain.controller = Controller()
        brain.recordedMovements = dict()
        brain.readRecordings()
    
    # read all recording files
    def readRecordings(brain):
        recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
        recordingNames = os.listdir(recordingsPath)
        recordingNames = [rn[0:-4] for rn in recordingNames if (os.path.isfile(recordingsPath + '/' + rn)) and (rn.endswith(".txt"))]
        for rn in recordingNames:
            brain.recordedMovements[rn] = Recording(rn)
    
    # record user movement to file
    def recordMovement(brain, recordRate, duration):
        moveTimeline = []
        frame = 0
        secDone = 0
        if (duration == 0):
            print("  (Press Q or Ctrl+C to stop)")
        print()
        try:
            while((duration == 0) or (frame < recordRate * duration)):
                moveTimeline.append(brain.convertToServoVals(brain.controller.getSensors()))
                if keyboard.is_pressed("q"):
                    break
                if (secDone == recordRate):
                    print("\n")
                    secDone = 0
                print(".", end = "")
                sys.stdout.flush()
                frame += 1
                secDone += 1
                time.sleep(1.0 / recordRate)
        except KeyboardInterrupt:
            pass
        print(f"\n\n{frame} frame(s) memorized.")
        print("\nCan you describe what you just did?\n")
        moveName = input("> ")
        recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
        moveFullPath = os.path.join(recordingsPath, moveName + ".txt")
        moveFile = open(moveFullPath, "w")
        moveFile.write(f"{recordRate}")
        for frameData in moveTimeline:
            moveFile.write(f"\n{frameData}")
        moveFile.close()
        newRecording = Recording(moveName)
        newRecording.timeline = moveTimeline
        brain.recordedMovements[moveName] = newRecording
        print("\nCool! Armold now knows how to " + moveName + ".")
        return
    
    # playback movement on robot
    def playbackMovement(brain, moveName, playbackRate, loop):
        print("  (Press Q or Ctrl+C to stop)")
        print()
        frame = 0
        secDone = 0
        movement = brain.recordedMovements[moveName]
        recLen = round(len(movement.timeline) * (1.0 / playbackRate), 2)
        try:
            while True:
                while(frame < len(movement.timeline)):
                    if keyboard.is_pressed("q"):
                        break
                    if (frame % playbackRate == 0):
                        print(f"{recLen - secDone} second(s) left...")
                        secDone += 1
                    brain.robot.setServos(movement.getServosAtTime(frame))
                    frame += 1
                    time.sleep(1.0 / refreshRate)
                if loop:
                    frame = 0
                    secDone = 0
                else:
                    break
        except KeyboardInterrupt:
            pass
        print(f"\nArmold is done performing '{moveName}!'")
        return

    # follow user movements on robot
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
    # initialization
    def __init__(recording, filename):
        recording.filename = filename
        recording.originalRate = 1
        recording.timeline = []
        recording.readRecordingFromFile(recording.filename)

    # convert file lines to data frames
    def readRecordingFromFile(recording, filename):
        recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
        moveFullPath = os.path.join(recordingsPath, recording.filename + ".txt")
        moveFile = open(moveFullPath, "r")
        try:
            rateVal = moveFile.readline()
            recording.originalRate = float(rateVal)
            for frame in moveFile:
                recording.timeline.append(json.loads(frame))
        except ValueError:
            recording.originalRate = 1
            print(f"unable to load recording file for {filename}")
        moveFile.close()
        return
    
    # gets data frame at time
    def getServosAtTime(recording, time):
        return recording.timeline[time]

class Robot:
    # initialization
    def __init__(robot):
        robot.servoPins = dict()
        robot.createServoConnections()
    
    # establishes servo pins
    def createServoConnections(robot):
        robot.servoPins["shoulder"] = 4
        robot.servoPins["elbow"] = 12
        return

    # sets servos to new positions
    def setServos(robot, newVals):
        for servoname, pin in robot.servoPins.items():
            if servoname in newVals.keys():
                pi.set_servo_pulsewidth(pin, newVals[servoname])
        return

class Controller:
    # initialization
    def __init__(controller):
        controller.sensorPins = dict()
        controller.createSensorConnections()
    
    # establishes sensor pins
    def createSensorConnections(controller):
        controller.sensorPins["shoulder"] = 4
        controller.sensorPins["elbow"] = 12
        return

    # gets current sensor positions
    def getSensors(controller):
        return

# main loop
pi = pigpio.pi()
brain = ArmoldBrain()
print("Armold is awake...")
while True:
    time.sleep(0.25)
    print("\nTell Armold what to do!",
            "\nCommands are:",
            "\n- (s) study movement",
            "\n- (p) perform movement",
            "\n- (l) mirror live movement",
            "\n- (t) test servo",
            "\n- (q) quit\n")
    command = input("> ")
    # study movement
    if(command == "s"):
        print("\nYou told Armold to study your movements.")
        # get recording rate
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
        # get recording duration
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
    # playback movement
    elif(command == "p"):
        print("\nYou told Armold to perform a movement.")
        # get movement name
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
        # get playback rate
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
        # get loop
        print("\nLoop the movement? (Y for yes, enter for no)\n")
        loopinput = input("> ")
        loop = False
        if (loopinput == "y"):
            loop = True
        print("\n- Armold is going to " + moveinput + "!")
        brain.playbackMovement(moveinput, refreshRate, loop)
    # mirror movement
    elif(command == "l"):
        print("\nYou told Armold to mirror your movements in real-time.")
        # get mirror rate
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
        print("\n- Armold is mirroring your movements!")
        brain.realtimeMovement(refreshRate)
    # test servo pin
    elif(command == "t"):
        print("\nYou told Armold to test a servo.")
        print("\nWhich pin is the servo on?")
        pininput = input("\n> ")
        try:
            pinnum = int(pininput)
            val = 1500
            rate = 20
            pi.set_servo_pulsewidth(pinnum, val)
            while True:
                time.sleep(0.01)
                pi.set_servo_pulsewidth(pinnum, val)
                val += rate
                if (val > 2500):
                    val = 1500
                    rate =-20
                if (val < 500):
                    val = 1500
                    rate = 20
        except ValueError:
            print("\nInvalid values provided.")
        except KeyboardInterrupt:
            print("\nEnding loop...")
    # quit
    elif(command == "q"):
        print("\n- Armold says 'Bye!'\n")
        break
    # invalid command
    else:
        print("\n- Armold doesn't know what '" + command + "' means...")