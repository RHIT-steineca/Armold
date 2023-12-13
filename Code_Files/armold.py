import os, sys, time, json
import paramiko
import tkinter as tk

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
            print("  (Press Ctrl+C to stop)")
        print()
        try:
            while((duration == 0) or (frame < recordRate * duration)):
                moveTimeline.append(brain.convertToServoVals(brain.controller.getSensors()))
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
        with open(moveFullPath, "w") as moveFile:
            moveFile.write(f"{recordRate}")
            for frameData in moveTimeline:
                moveFile.write(f"\n{frameData}")
        newRecording = Recording(moveName)
        newRecording.timeline = moveTimeline
        brain.recordedMovements[moveName] = newRecording
        print("\nCool! Armold now knows how to " + moveName + ".")
        return
    
    # playback movement on robot
    def playbackMovement(brain, moveName, playbackRate, loop):
        print("  (Press Ctrl+C to stop)")
        print()
        frame = 0
        secDone = 0
        movement = brain.recordedMovements[moveName]
        recLen = round(len(movement.timeline) * (1.0 / playbackRate), 2)
        try:
            while True:
                while(frame < len(movement.timeline)):
                    if (frame % playbackRate == 0):
                        print(f"{recLen - secDone} second(s) left...")
                        secDone += 1
                    try:
                        brain.robot.setServos(movement.getServosAtTime(frame), playbackRate)
                    except Exception:
                        raise Exception("SSH Disconnected.")
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
        print("  (Press Ctrl+C to stop)")
        print()
        try:
            while(True):
                try:
                    brain.robot.setServos(brain.convertToServoVals(brain.controller.getSensors()), refreshRate)
                except Exception:
                    raise Exception("SSH Disconnected.") 
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
        try:
            with open(moveFullPath, "r") as moveFile:
                rateVal = moveFile.readline()
                recording.originalRate = float(rateVal)
                for frame in moveFile:
                    recording.timeline.append(json.loads(frame))
        except ValueError:
            recording.originalRate = 1
            print(f"unable to load recording file for {filename}")
        return
    
    # gets data frame at time
    def getServosAtTime(recording, time):
        return recording.timeline[time]

class Robot:
    # initialization
    def __init__(robot):
        robot.servoPins = ["shoulderCB","shoulderR","shoulderLR","elbow","wrist","finger1","finger2","finger3","finger4","finger5"]

    # sets servos to new positions
    def setServos(robot, newVals, refreshRate):
        robovalString = str(refreshRate)
        for servoname in robot.servoPins:
            if servoname in newVals.keys():
                robovalString += f"\n{servoname},{newVals[servoname]}"
        try:
            checkSSHconnection(ssh)
            testEnv.updateVals(newVals)
            ssh.exec_command(f'sudo echo "{robovalString}" > robovals.txt', timeout = 1.0 / refreshRate)
        except Exception:
            raise Exception("SSH Disconnected.")
        return

class Controller:
    # initialization
    def __init__(controller):
        controller.sensorPins = dict()
        controller.createSensorConnections()
    
    # establishes sensor pins
    def createSensorConnections(controller):
        controller.sensorPins["shoulderCB"] = 0
        controller.sensorPins["shoulderR"] = 1
        controller.sensorPins["shoulderLR"] = 2
        controller.sensorPins["elbow"] = 3
        controller.sensorPins["wrist"] = 4
        controller.sensorPins["finger1"] = 5
        controller.sensorPins["finger2"] = 6
        controller.sensorPins["finger3"] = 7
        controller.sensorPins["finger4"] = 8
        controller.sensorPins["finger5"] = 9
        return

    # gets current sensor positions
    def getSensors(controller):
        return

def checkSSHconnection(ssh):
    if not ssh.get_transport().is_active():
        raise Exception("SSH disconnected")
    return

class TestEnvironment:
    def __init__(testenv):
        testenv.valpairs = dict()
        testenv.labelpairs = dict()
        for servoName in brain.robot.servoPins:
            testenv.valpairs[servoName] = 2500
        testenv.setupWindow()
    
    def setupWindow(testenv):
        testenv.window = tk.Tk()
        testenv.window.title("Armold Testing Environment")
        testenv.buttonFrame = tk.Frame(testenv.window)
        testenv.buttonFrame.pack(side="top", expand=True, fill="x")
        rebootButton = tk.Button(testenv.buttonFrame, text="Reboot Armold\n(Restart Pi)", padx=30, pady=30, command=lambda : os.system("sudo reboot")).pack(side="left", expand=True, fill="both")
        closeButton = tk.Button(testenv.buttonFrame, text="Close Testing Window", padx=30, pady=30, command=lambda : testenv.closeWindow()).pack(side="right", expand=True, fill="both")
        testenv.frame = tk.Frame(testenv.window)
        testenv.frame.pack(side="left", expand=True, fill="both", pady=30)
        for servoName, servoVal in testenv.valpairs.items():
            label = tk.Label(testenv.frame, text=f"{servoName}: {servoVal} Volts, {testenv.convertValToAngle(servoName, servoVal)} Degrees")
            testenv.labelpairs[servoName] = label
            label.pack(side="top", pady=2)
        testenv.window.geometry('450x450+0+0')
        testenv.window.protocol("WM_DELETE_WINDOW", lambda : testenv.forcedWindowClosed())
        testenv.window.withdraw()
    
    def updateVals(testenv, newVals):
        for servoname, val in testenv.valpairs.items():
            if servoname in newVals.keys():
                testenv.valpairs[servoname] = newVals[servoname]
        testenv.updateWindow()
    
    def updateWindow(testenv):
        for servoName, servoVal in testenv.valpairs.items():
            if servoName in testenv.labelpairs.keys():
                label = testenv.labelpairs[servoName]
                label.config(text=f"{servoName}: {servoVal} Volts, {testenv.convertValToAngle(servoName, servoVal)} Degrees")
                label.pack()
        testenv.frame.pack()
        testenv.window.update()

    def convertValToAngle(testenv, servoName, servoValue):
        minVal = 500
        maxVal = 2500
        minDeg = 0
        maxDeg = 360
        if (servoName == "shoulderCB"):
            maxDeg = 45
        if (servoName == "shoulderR"):
            maxDeg = 180
        if (servoName == "shoulderLR"):
            maxDeg = 90
        if (servoName == "elbow"):
            maxDeg = 150
        if (servoName == "wrist"):
            maxDeg = 180
        if (servoName == "finger1"):
            maxDeg = 1
        if (servoName == "finger2"):
            maxDeg = 1
        if (servoName == "finger3"):
            maxDeg = 1
        if (servoName == "finger4"):
            maxDeg = 1
        if (servoName == "finger5"):
            maxDeg = 1
        valRange = maxVal-minVal
        degRange = maxDeg-minDeg
        percentValue = round(float((servoValue - minVal) / valRange), 1)
        degValue = minDeg + (percentValue * degRange)
        return degValue
    
    def showWindow(testenv):
        testenv.window.deiconify()
        testenv.updateWindow()
    
    def closeWindow(testenv):
        testenv.window.withdraw()
        
    def forcedWindowClosed(testenv):
        testenv.window.destroy()
        testenv.setupWindow()

# main loop
brain = ArmoldBrain()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
testEnv = TestEnvironment()
quitCommanded = True
print("Armold is awake! \nNow looking for its arm...")
while (quitCommanded):
    try:
        ssh.connect("ArmoldSecondary", username="pi", password="Armold", timeout=15)
        print("\nArm found! Armold is ready to go!")
        while True:
            checkSSHconnection(ssh)
            defaultRobotVals = dict()
            for servoname in brain.robot.servoPins:
                defaultRobotVals[servoname] = 2500
            brain.robot.setServos(defaultRobotVals, 1)
            time.sleep(0.25)
            print("\nTell Armold what to do!",
                    "\nCommands are:",
                    "\n- (s) study movement",
                    "\n- (p) perform movement",
                    "\n- (l) mirror live movement",
                    "\n- (t) test pin connection",
                    "\n- (e) show testing environment",
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
                if (loopinput == "Y"):
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
                print("\nYou told Armold to test a pin.")
                print("\nWhich pin should be tested?")
                pininput = input("\n> ")
                print("\nIs the pin connected to a sensor or servo?")
                pintype = input("\n> ")
                try:
                    pinnum = int(pininput)
                    print(f"\nTesting pin #{pinnum}...")
                    print("  (Press Ctrl+C to stop)")
                    if (pintype == "sensor"):
                        while True:
                            print(f"print sensor val")
                    elif (pintype == "servo"):
                        val = 1500
                        rate = 20
                        # set initial servo val
                        while True:
                            time.sleep(0.01)
                            # set servo val
                            val += rate
                            if (val > 2500):
                                val = 1500
                                rate =-20
                            if (val < 500):
                                val = 1500
                                rate = 20
                    else:
                        print("Huh?")
                except ValueError:
                    print("\nInvalid values provided.")
                except KeyboardInterrupt:
                    print("\nEnding loop...")
            # show testing environment
            elif(command == "e"):
                print("\nYou told Armold to show its testing environment.")
                testEnv.showWindow()
            # quit
            elif(command == "q"):
                print("\n- Armold says 'Bye!'\n")
                quitCommanded = False
                break
            # invalid command
            else:
                print("\n- Armold doesn't know what '" + command + "' means...")
    except Exception:
        print("\nSorry, Armold is having trouble finding its arm... trying again...")
    finally:
        ssh.close()