import os, sys, time, json, secrets, string, math
import paramiko
import tkinter as tk
import pyfirmata

# joint mapping
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":1333,"shoulderLR":270,"elbow":235,"wrist":230,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":100}
servoMaxRange = {"shoulderCB":270,"shoulderR":1333,"shoulderLR":270,"elbow":270,"wrist":270,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}

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
    def recordMovement(brain, refreshRate, duration):
        moveTimeline = []
        frame = 0
        secDone = 0
        if (duration == 0):
            print("  (Press Ctrl+C to stop)")
        print()
        try:
            lastFrame = time.time()
            while((duration == 0) or (frame < refreshRate * duration)):
                if (time.time() - lastFrame >= 1.0 / refreshRate):
                    lastFrame = time.time()
                    currentFrameData = brain.convertToServoVals(brain.controller.getSensors())
                    brain.robot.setServos(currentFrameData, refreshRate)
                    moveTimeline.append(currentFrameData)
                    if (secDone == refreshRate):
                        print("\n")
                        secDone = 0
                    print(".", end = "")
                    sys.stdout.flush()
                    frame += 1
                    secDone += 1
        except KeyboardInterrupt:
            pass
        print(f"\n\n{frame} frame(s) memorized.")
        print("\nCan you describe what you just did?\n")
        rawMoveName = input("> ")
        moveName = rawMoveName.replace(" ", "_")
        recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
        moveFullPath = os.path.join(recordingsPath, moveName + ".txt")
        with open(moveFullPath, "w") as moveFile:
            moveFile.write(f"{float(refreshRate)}")
            for frameData in moveTimeline:
                framestring = str(frameData).replace("'", '"')
                moveFile.write(f"\n{framestring}")
        newRecording = Recording(moveName)
        newRecording.timeline = moveTimeline
        brain.recordedMovements[moveName] = newRecording
        print("\nCool! Armold now knows how to " + rawMoveName + ".")
        return
    
    # playback movement on robot
    def playbackMovement(brain, moveName, refreshRate, loop):
        print("  (Press Ctrl+C to stop)")
        print()
        frame = 0
        secDone = 0
        movement = brain.recordedMovements[moveName]
        recLen = round(len(movement.timeline) * (1.0 / refreshRate), 2)
        try:
            while True:
                lastFrame = time.time()
                while(frame < len(movement.timeline)):
                    if (time.time() - lastFrame >= 1.0 / refreshRate):
                        lastFrame = time.time()
                        if (frame % refreshRate == 0):
                            print(f"{round(recLen - secDone, 1)} second(s) left...")
                            secDone += 1
                        try:
                            brain.robot.setServos(movement.getServosAtTime(frame), refreshRate)
                        except Exception as error:
                            raise error
                        frame += 1
                if loop:
                    frame = 0
                    secDone = 0
                    try:
                        brain.robot.setServos(movement.getServosAtTime(0), 0.5)
                    except Exception as error:
                        raise error
                    print(f"Looping to {moveName} start...")
                    time.sleep(1)
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
            lastFrame = time.time()
            while True:
                if (time.time() - lastFrame >= 1.0 / refreshRate):
                    lastFrame = time.time()
                    try:
                        brain.robot.setServos(brain.convertToServoVals(brain.controller.getSensors()), refreshRate)
                    except Exception as error:
                        raise error
        except KeyboardInterrupt:
            pass
        return
    
    # convert values from sensor -> servo
    # returns actual servo angles, robot program handles converting to arduino steps
    def convertToServoVals(brain, sensorVals):
        # TODO setup convertion ratios
        servoVals = dict()
        for name, val in sensorVals.items():
            minDeg = limitedMinDegs[name]
            calcAngle = (val * limitedMaxDegs[name]) - minDeg
            # reverse directions
            if ("fingerPTR" in name or "fingerMDL" in name or "elbow" in name):
                calcAngle = limitedMaxDegs[name] - calcAngle
            # # finger open/closed only
            # if ("finger" in name):
            #     if (calcAngle < 90):
            #         calcAngle = 0
            #     else:
            #         calcAngle = 180
            servoVals[name] = calcAngle
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
        robot.servoPins = ["shoulderCB","shoulderR","shoulderLR","elbow","wrist","fingerPTR","fingerMDL","fingerRNG","fingerPKY","fingerTHM"]

    # sets servos to new positions
    def setServos(robot, newVals, refreshRate):
        frameKey = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(math.floor(refreshRate) + 5))
        robovalString =  f'{str(frameKey)}\n{str(refreshRate)}'
        for servoname, newVal in newVals.items():
            if servoname in robot.servoPins:
                robovalString += f'\n"{servoname}",{newVal}'
        try:
            checkSSHconnection(ssh)
            testEnv.updateVals(newVals)
            # # TODO: FIX CHANNEL LATENCY / TOO MANY CHANNELS BEING CREATED
            # # Possible shell opening, single channel https://paramiko.lag.narkive.com/JmgWmTWn/how-do-i-execute-multiple-commands-in-a-single-channel#post15
            # # help for channel block checking https://stackoverflow.com/questions/28485647/wait-until-task-is-completed-on-remote-machine-through-python
            # stdin, stdout, stderr = ssh.exec_command(f'sudo echo "{robovalString}" > robovals.txt', timeout=1.0 / refreshRate)
            # stdout.channel.recv_stderr_ready()
            # stdout.channel.close()
            transport = ssh.get_transport()
            channel = transport.open_session()
            channel.settimeout(1.0 / refreshRate)
            channel.exec_command(f'sudo echo "{robovalString}" > robovals.txt')
            channel.close()
        except Exception as error:
            # print(f"{error}")
            print("-frame dropped-")
            pass 
        return

class Controller:
    # initialization
    def __init__(controller):
        controller.sensorConnections = dict()
        controller.createSensorConnections()
    
    # establishes sensor pins
    def createSensorConnections(controller):
        # TODO: update channels for potentiometer connections
        board = pyfirmata.Arduino('/dev/ttyACM0')
        it = pyfirmata.util.Iterator(board)
        it.start()
        pinMapping = {"fingerPTR":5,"fingerMDL":5,"fingerRNG":5,"fingerPKY":5,"fingerTHM":5}
        connections = dict()
        for i in range(6):
            connections[i] = board.get_pin(f'a:{i}:i')
        for name, pin in pinMapping.items():
            controller.sensorConnections[name] = connections[pin]
        return

    # gets current sensor positions
    def getSensors(controller):
        readings = dict()
        for name, connection in controller.sensorConnections.items():
            readings[name] = connection.read()
        return readings

def checkSSHconnection(ssh):
    if not ssh.get_transport().is_active():
        raise Exception("SSH connection severed")
    return

class TestEnvironment:
    def __init__(testenv):
        testenv.valpairs = dict()
        testenv.labelpairs = dict()
        for servoName in brain.robot.servoPins:
            testenv.valpairs[servoName] = 0
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
            label = tk.Label(testenv.frame, text=f"{servoName}: {round(testenv.convertAngleToVal(servoName, servoVal), 1)} Steps, {round(servoVal, 1)} Degrees")
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
                label.config(text=f"{servoName}: {round(testenv.convertAngleToVal(servoName, servoVal), 1)} Steps, {round(servoVal, 1)} Degrees")
                label.pack()
        testenv.frame.pack()
        testenv.window.update()

    def convertAngleToVal(testenv, servoName, sensorAngle):
        minVal = arduinoMinVals[servoName]
        maxVal = arduinoMaxVals[servoName]
        minDeg = limitedMinDegs[servoName]
        maxDeg = servoMaxRange[servoName]
        valRange = maxVal-minVal
        degRange = maxDeg-minDeg
        calcVal = sensorAngle * valRange / degRange
        return calcVal
    
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
ssh.set_combine_stderr = True
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
                defaultRobotVals[servoname] = 0.0
            brain.robot.setServos(brain.convertToServoVals(defaultRobotVals), 4)
            time.sleep(0.25)
            print("\nTell Armold what to do!",
                    "\nCommands are:",
                    "\n- (s) study movement",
                    "\n- (p) perform movement",
                    "\n- (l) mirror live movement",
                    "\n- (e) show testing environment",
                    "\n- (z) zero stepper tracked position"
                    "\n- (q) quit\n")
            command = input("> ")
            # study movement
            if(command == "s"):
                print("\nYou told Armold to study your movements.")
                # get recording rate
                while True:
                    print("\nRate of recording? (Hz < 30)\n")
                    try:
                        rateinput = input("> ")
                        refreshRate = int(rateinput)
                        if (refreshRate >= 1 and refreshRate < 30):
                            break
                        else:
                            print("\nThe rate needs to be at least 1 but less than 30, try again.")
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
                        name = rn.replace("_", " ")
                        print(f"- {name} ({len(rec.timeline)} frames, {round(len(rec.timeline) * (1.0 / rec.originalRate), 2)} secs at {rec.originalRate} Hz originally)")
                    print()
                    rawMoveInput = input("> ")
                    moveInput = rawMoveInput.replace(" ", "_")
                    if moveInput in brain.recordedMovements:
                        break
                    else:
                        print("\n'" + moveinput + "' isn't a movement Armold has memorized, try again.")
                # get playback rate
                while True:
                    print("\nRate of playback? (Hz < 30)\n")
                    try:
                        rateinput = input("> ")
                        refreshRate = int(rateinput)
                        if (refreshRate >= 1 and refreshRate < 30):
                            break
                        else:
                            print("\nThe rate needs to be at least 1 but less than 30, try again.")
                    except ValueError:
                        print("\n'" + rateinput + "' isn't a number, try again.")
                # get loop
                print("\nLoop the movement? (Y for yes, enter for no)\n")
                loopinput = input("> ")
                loop = False
                if (loopinput == "Y"):
                    loop = True
                print("\n- Armold is going to " + moveInput + "!")
                brain.playbackMovement(moveInput, refreshRate, loop)
            # mirror movement
            elif(command == "l"):
                print("\nYou told Armold to mirror your movements in real-time.")
                # get mirror rate
                while True:
                    print("\nRate of recording? (Hz)\n")
                    try:
                        rateinput = input("> ")
                        refreshRate = float(rateinput)
                        if (refreshRate >= 1 and refreshRate < 30):
                            break
                        else:
                            print("\nThe rate needs to be at least 1 but less than 30, try again.")
                    except ValueError:
                        print("\n'" + rateinput + "' isn't a number, try again.")
                print("\n- Armold is mirroring your movements!")
                brain.realtimeMovement(refreshRate)
            # show testing environment
            elif(command == "e"):
                print("\nYou told Armold to show its testing environment.")
                testEnv.showWindow()
            # zero stepper tracking
            elif(command == "z"):
                print("\nYou told Armold to zero its stepper motor tracking.")
                transport = ssh.get_transport()
                channel = transport.open_session()
                channel.settimeout(1.0)
                channel.exec_command(f'sudo echo "RESET\nRESET" > robovals.txt')
                channel.close()
            # quit
            elif(command == "q"):
                print("\n- Armold says 'Bye!'\n")
                quitCommanded = False
                break
            # invalid command
            else:
                print("\n- Armold doesn't know what '" + command + "' means...")
    except Exception as error:
        print(f"\nSorry, Armold is having trouble finding its arm...\n({error})\ntrying again...")
        time.sleep(5)
    finally:
        ssh.close()