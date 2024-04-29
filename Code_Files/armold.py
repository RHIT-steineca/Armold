import os, sys, time, json, secrets, string, math
import mqtt_helper
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from PIL import ImageTk
import pyfirmata

# joint mapping
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":25,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":2000,"shoulderLR":270,"elbow":235,"wrist":230,"fingerPTR":180,"fingerMDL":160,"fingerRNG":180,"fingerPKY":180,"fingerTHM":120}
actuatorMaxRange = {"shoulderCB":270,"shoulderR":2000,"shoulderLR":270,"elbow":270,"wrist":270,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}
REFRESH_RATE = 20
RECORDING_MAX_SECS = 300

class ArmoldBrain:
    # initialization
    def __init__(brain):
        brain.robot = Robot()
        brain.controller = Controller()
        brain.recordedMovements = dict()
        brain.newMoveTimeline = []
        brain.readRecordings()
    
    # read all recording files
    def readRecordings(brain):
        recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
        recordingNames = os.listdir(recordingsPath)
        recordingNames = [rn[0:-4] for rn in recordingNames if (os.path.isfile(recordingsPath + '/' + rn)) and (rn.endswith(".txt"))]
        for rn in recordingNames:
            brain.recordedMovements[rn] = Recording(rn)
    
    # record user movement
    def recordMovement(brain, refreshRate):
        brain.newMoveTimeline = []
        frame = 0
        lastFrame = time.time()
        while(frame < refreshRate * RECORDING_MAX_SECS):
            if(armoldGUI.state != "recording"):
                return
            if (time.time() - lastFrame >= 1.0 / refreshRate):
                lastFrame = time.time()
                currentFrameData = brain.convertToActuatorVals(brain.controller.getSensors())
                try:
                    brain.robot.setActuators(currentFrameData, refreshRate)
                except Exception as error:
                    handleConnectionError()
                    armoldGUI.stopRecording()
                    return
                brain.newMoveTimeline.append(currentFrameData)
                frame += 1
            armoldGUI.window.update()
        armoldGUI.stopRecording()
    
    # save latest recorded movement to file
    def saveRecordedMovement(brain, name, refreshRate):
        try:
            recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
            moveFullPath = os.path.join(recordingsPath, name + ".txt")
            with open(moveFullPath, "w") as moveFile:
                moveFile.write(f"{float(refreshRate)}")
                for frameData in brain.newMoveTimeline:
                    framestring = str(frameData).replace("'", '"')
                    moveFile.write(f"\n{framestring}")
            newRecording = Recording(name)
            newRecording.timeline = brain.newMoveTimeline
            newRecording.originalRate = refreshRate
            brain.newMoveTimeline = []
            brain.recordedMovements[name] = newRecording
            return
        except Exception as error:
            print(f"Can't save recording\n{error}")
    
    # delete a movement from storage
    def deleteMovement(brain, moveName):
        try:
            recordingsPath = "//home//pi//Armold//Code_Files//Recordings//"
            moveFullPath = os.path.join(recordingsPath, moveName + ".txt")
            if os.path.exists(moveFullPath):
                os.remove(moveFullPath)
                del brain.recordedMovements[moveName]
        except Exception as error:
            return
    
    # playback movement on robot
    def playbackMovement(brain, moveName, refreshRate):
        frame = 0
        movement = brain.recordedMovements[moveName]
        while (armoldGUI.state == "playback"):
            lastFrame = time.time()
            while(frame < len(movement.timeline)):
                if (time.time() - lastFrame >= 1.0 / refreshRate):
                    lastFrame = time.time()
                    try:
                        brain.robot.setActuators(movement.getActuatorsAtTime(frame), refreshRate)
                    except Exception as error:
                        handleConnectionError()
                        return
                    curLen = math.floor(frame * (1.0 / refreshRate))
                    displaysecs = curLen%60
                    if(displaysecs < 10):
                        displaysecs = f"0{displaysecs}"
                    current = f"{math.floor(curLen/60)}:{displaysecs}"
                    recLen = math.floor(len(movement.timeline) * (1.0 / refreshRate))
                    displaysecs = recLen%60
                    if(displaysecs < 10):
                        displaysecs = f"0{displaysecs}"
                    duration = f"{math.floor(recLen/60)}:{displaysecs}"
                    armoldGUI.updatePlaybackDuration(f"{current}\n/{duration}")
                    armoldGUI.window.update()
                    frame += 1
            if armoldGUI.playbackLoop:
                frame = 0
                try:
                    brain.robot.setActuators(movement.getActuatorsAtTime(0), 0.5)
                except Exception as error:
                    handleConnectionError()
                    return
                time.sleep(1)
            else:
                armoldGUI.stopPlayback()
                return
        return

    # follow user movements on robot
    def realtimeMovement(brain, refreshRate):
        lastFrame = time.time()
        while (armoldGUI.state == "mirror"):
            if (time.time() - lastFrame >= 1.0 / refreshRate):
                lastFrame = time.time()
                try:
                    brain.robot.setActuators(brain.convertToActuatorVals(brain.controller.getSensors()), refreshRate)
                except Exception as error:
                    handleConnectionError()
                    return
            armoldGUI.window.update()
        return
    
    # convert values from sensor -> actuator
    # returns actual actuator angles, robot program handles converting to arduino steps
    def convertToActuatorVals(brain, sensorVals):
        actuatorVals = dict()
        for name, val in sensorVals.items():
            minDeg = limitedMinDegs[name]
            calcAngle = (val * limitedMaxDegs[name]) - minDeg
            # reverse directions
            if ("fingerTHM" in name or "shoulderLR" in name or "elbow" in name):
                calcAngle = limitedMaxDegs[name] - calcAngle
            # # finger open/closed only
            # if ("finger" in name):
            #     if (calcAngle < 90):
            #         calcAngle = 0
            #     else:
            #         calcAngle = 180
            actuatorVals[name] = calcAngle
        return actuatorVals

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
    def getActuatorsAtTime(recording, time):
        return recording.timeline[time]

class Robot:
    # initialization
    def __init__(robot):
        robot.actuatorPins = ["shoulderCB","shoulderR","shoulderLR","elbow","wrist","fingerPTR","fingerMDL","fingerRNG","fingerPKY","fingerTHM"]

    # sets actuators to new positions
    def setActuators(robot, newVals, refreshRate):
        frameKey = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(math.floor(refreshRate) + 5))
        actuatorCommand =  [frameKey,refreshRate,newVals]
        try:
            testEnv.updateVals(newVals)
            # TODO test this timeout works
            connection.client._connect_timeout = 1.0 / 2 * refreshRate
            connection.client.send_message("command", actuatorCommand)
        except Exception as error:
            print(error)
            print("-frame dropped-")
            pass 
        return
    
    def goHome(robot):
        defaultRobotVals = dict()
        for actuatorName in robot.actuatorPins:
            defaultRobotVals[actuatorName] = 0.0
            if("finger" in actuatorName):
                defaultRobotVals[actuatorName] = 1.0
        robot.setActuators(brain.convertToActuatorVals(defaultRobotVals), 4)

class Controller:
    # initialization
    def __init__(controller):
        controller.sensorConnections = dict()
        controller.createSensorConnections()
    
    # establishes sensor pins
    def createSensorConnections(controller):
        board = pyfirmata.ArduinoMega('/dev/ttyACM0')
        it = pyfirmata.util.Iterator(board)
        it.start()
        pinMapping = dict()
        valPath = "//home//pi//Armold//Code_Files//"
        pinsPath = os.path.join(valPath, "pins.txt")
        with open(pinsPath, "r") as pinFile:
            pinFile.readline()
            pinMapping = json.loads(pinFile.readline())
        connections = dict()
        for i in range(16):
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

class TestEnvironment:
    def __init__(testenv):
        testenv.valpairs = dict()
        testenv.labelpairs = dict()
        for actuatorName in brain.robot.actuatorPins:
            testenv.valpairs[actuatorName] = 0
        testenv.setupWindow()
    
    def setupWindow(testenv):
        testenv.window = tk.Toplevel()
        testenv.window.title("Testing Environment")
        testenv.frame = tk.Frame(testenv.window)
        testenv.frame.pack(side="left", expand=True, fill="both", pady=30)
        for actuatorName, actuatorVal in testenv.valpairs.items():
            label = tk.Label(testenv.frame, text=f"{actuatorName}: {round(testenv.convertAngleToVal(actuatorName, actuatorVal), 1)} Steps, {round(actuatorVal, 1)} Degrees")
            testenv.labelpairs[actuatorName] = label
            label.pack(side="top", pady=2)
        testenv.screenwidth = root.winfo_screenwidth()
        testenv.window.geometry(f'450x380+{testenv.screenwidth - 450}+0')
        testenv.window.protocol("WM_DELETE_WINDOW", lambda : testenv.forcedWindowClosed())
        testenv.window.withdraw()
    
    def updateVals(testenv, newVals):
        for actuatorname, val in testenv.valpairs.items():
            if actuatorname in newVals.keys():
                testenv.valpairs[actuatorname] = newVals[actuatorname]
        testenv.updateWindow()
    
    def updateWindow(testenv):
        for actuatorName, actuatorVal in testenv.valpairs.items():
            if actuatorName in testenv.labelpairs.keys():
                label = testenv.labelpairs[actuatorName]
                label.config(text=f"{actuatorName}: {round(testenv.convertAngleToVal(actuatorName, actuatorVal), 1)} Steps, {round(actuatorVal, 1)} Degrees", font=("Courier Prime", 14))
                label.pack()
        testenv.frame.pack()
        testenv.window.update()

    def convertAngleToVal(testenv, actuatorName, sensorAngle):
        minVal = arduinoMinVals[actuatorName]
        maxVal = arduinoMaxVals[actuatorName]
        minDeg = limitedMinDegs[actuatorName]
        maxDeg = actuatorMaxRange[actuatorName]
        valRange = maxVal-minVal
        degRange = maxDeg-minDeg
        calcVal = sensorAngle * valRange / degRange
        return calcVal
    
    def showWindow(testenv):
        testenv.closeWindow()
        testenv.window.deiconify()
        testenv.window.geometry(f'450x380+{testenv.screenwidth - 450}+0')
        testenv.updateWindow()
    
    def closeWindow(testenv):
        testenv.window.withdraw()
        
    def forcedWindowClosed(testenv):
        testenv.window.destroy()
        testenv.setupWindow()

class ArmoldGUI:
    def __init__(self):
        self.state = "disabled"
        self.stateText = "Armold is awake! \nNow looking for its arm..."
        self.playing = "NONE"
        self.playbackLoop = False
        # window setup
        self.window = root
        self.window.title("Armold")
        self.screenwidth = self.window.winfo_screenwidth()
        self.screenheight = self.window.winfo_screenheight()
        self.recordingsFrameWidth = 0.7 * self.screenwidth
        self.controlsFrameWidth = 0.3 * self.screenwidth
        self.borderPadding = 0.01 * self.screenheight
        self.window.geometry(f'{self.screenwidth}x{self.screenheight}+0+0')
        self.window.resizable(False, False)
        self.window.attributes('-fullscreen', True)
        self.window.protocol("WM_DELETE_WINDOW", lambda : self.closeWindow())
        self.fillWindow()

    def fillWindow(self):
        self.windowFrame = tk.Frame(self.window).pack()
        # recording area frames
        self.recordingsframeborder = tk.Frame(self.windowFrame, width=self.recordingsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.recordingsframeborder.pack(side="left", expand=True, fill="both")
        self.recordingsframe = ctk.CTkFrame(self.recordingsframeborder, border_color="#BABFC9", fg_color="#BABFC9", border_width=self.borderPadding, corner_radius=15)
        self.recordingsframe.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # recording area elements
        self.statusAreaFrame = ctk.CTkFrame(self.recordingsframe, fg_color="#EAF1FF", bg_color="#BABFC9", border_width=0, corner_radius=15)
        self.statusAreaFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        self.recordingsList = ctk.CTkScrollableFrame(self.recordingsframe, bg_color="#BABFC9", fg_color="#BABFC9", scrollbar_fg_color="#FFFFFF", scrollbar_button_color="#5D6D8B", scrollbar_button_hover_color="#427FF6", corner_radius=15)
        self.recordingsList._scrollbar.configure(width=10*self.borderPadding, corner_radius=30)
        self.recordingsList.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # controls area frames
        self.controlsframeborder = tk.Frame(self.windowFrame, width=self.controlsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.controlsframeborder.pack(side="right", expand=False, fill="both")
        canvas = tk.Canvas(self.controlsframeborder, width=self.controlsFrameWidth, height=self.controlsFrameWidth, bd=0, highlightthickness=0, background="#FFFFFF")
        canvas.pack(side="top", padx=(2*self.borderPadding, self.borderPadding), pady=self.borderPadding, expand=False, fill="both")
        logoImg = Image.open("gui_icons/armold_logo_glow.png")
        logoImg = logoImg.resize((round(self.controlsFrameWidth),round(self.controlsFrameWidth)), Image.ANTIALIAS)
        canvas.logo = ImageTk.PhotoImage(logoImg)
        canvas.create_image(0,0, anchor="nw", image=canvas.logo)
        self.controlsframe = ctk.CTkFrame(self.controlsframeborder, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        self.controlsframe.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # controls area elements
        # record button
        self.recordButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        self.recordButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.recordButtonMargin = tk.Frame(self.recordButtonFrame, width=self.controlsFrameWidth, background="#FFFFFF")
        self.recordButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # mirror button
        self.mirrorButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        self.mirrorButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.mirrorButtonMargin = tk.Frame(self.mirrorButtonFrame, width=self.controlsFrameWidth, background="#FFFFFF")
        self.mirrorButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # debug and shutdown buttons
        tekButtonMargin = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        tekButtonMargin.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        debugButtonImage = ctk.CTkImage(Image.open("gui_icons/debug.png"), size=(3*round(self.borderPadding),3*round(self.borderPadding)))
        debugButton = ctk.CTkButton(tekButtonMargin, height=5*self.borderPadding, image=debugButtonImage, text="Show Debug Info", font=("Courier Prime", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.showDebugWindow())
        debugButton.pack(side="left", expand=False, fill="y")
        powerButtonImage = ctk.CTkImage(Image.open("gui_icons/power.png"), size=(3*round(self.borderPadding),3*round(self.borderPadding)))
        closeButton = ctk.CTkButton(tekButtonMargin, height=5*self.borderPadding, image=powerButtonImage, text="Shut Down", font=("Courier Prime", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.closeWindow())
        closeButton.pack(side="right", expand=False, fill="y")

        self.updateGraphics()
        
    def updateGraphics(self):
        # clear old state-dependent graphics
        for child in self.statusAreaFrame.winfo_children() + self.recordingsList.winfo_children() + self.recordButtonMargin.winfo_children() + self.mirrorButtonMargin.winfo_children():
            child.destroy()
        
        # set status message
        self.statusMessage = tk.Label(self.statusAreaFrame, text=self.stateText, font=("Courier Prime", 24), background="#EAF1FF", justify="left")
        self.statusMessage.pack(side="left", padx=2*self.borderPadding, pady=2*self.borderPadding, expand=False, fill="both")
        
        if(self.state == "idle"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#FFFFFF", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier Prime", 26), text_color="#000000", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#DDDDDD", bg_color="#FFFFFF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier Prime", 24), text_color="#000000")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda rn=rn: self.startPlayback(rn))
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda rn=rn: self.deleteRecording(rn))
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier Prime", 28), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startRecording())
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier Prime", 28), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startMirror())
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        elif(self.state == "mirror"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#FFFFFF", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier Prime", 26), text_color="#000000", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#DDDDDD", bg_color="#FFFFFF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier Prime", 24), text_color="#000000")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda rn=rn: self.startPlayback(rn))
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda rn=rn: self.deleteRecording(rn))
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier Prime", 28), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startRecording())
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Stop Control", font=("Courier Prime", 28), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.stopMirror())
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#427FF6", outline="#FFFFFF")
        elif(self.state == "playback"):
            # duration and loop buttons
            self.loopButtonMargin = tk.Frame(self.statusAreaFrame, width=self.controlsFrameWidth, background="#EAF1FF")
            self.loopButtonMargin.pack(side="right", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
            self.playbackDuration = tk.Label(self.loopButtonMargin, text="0:00\n/0:00", font=("Courier Prime", 20), background="#EAF1FF", bd=0, highlightthickness=0, justify="right")
            self.playbackDuration.pack(side="left", expand=True, fill="both", padx=self.borderPadding)
            loopButtonImage = ctk.CTkImage(Image.open("gui_icons/loop.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            if(self.playbackLoop == True):
                self.loopButton = ctk.CTkButton(self.loopButtonMargin, image=loopButtonImage, text="Loop", font=("Courier Prime", 32), text_color="#FFB800", fg_color="#FFD9A0", bg_color="#EAF1FF", hover_color="#FFD9A0", border_color="#FFB800", border_width=self.borderPadding, corner_radius=15, command=lambda : self.toggleLoop())
            else:
                self.loopButton = ctk.CTkButton(self.loopButtonMargin, image=loopButtonImage, text="Loop", font=("Courier Prime", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#EAF1FF", hover_color="#FFD9A0", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.toggleLoop())
            self.loopButton.pack(side="right", expand=False, fill="both")
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                niceName = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                if(rn == self.playing):
                    playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#EAF1FF", bg_color="#BABFC9", corner_radius=15)
                    playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                    nameLabel = ctk.CTkLabel(playbackFrame, text=niceName, font=("Courier Prime", 26), text_color="#000000", justify="left")
                    nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                    playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#EAF1FF", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                    playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier Prime", 24), text_color="#000000")
                    durationLabel.pack(side="right")
                    stopButtonImage = ctk.CTkImage(Image.open("gui_icons/stop.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    stopButton = ctk.CTkButton(playbackButtonsFrame, image=stopButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#BDBDBD", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.stopPlayback())
                    stopButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                    deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                else:
                    playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#DADADA", bg_color="#BABFC9", corner_radius=15)
                    playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                    nameLabel = ctk.CTkLabel(playbackFrame, text=niceName, font=("Courier Prime", 26), text_color="#BDBDBD", justify="left")
                    nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                    playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                    playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier Prime", 24), text_color="#BDBDBD")
                    durationLabel.pack(side="right")
                    playButtonImage = ctk.CTkImage(Image.open("gui_icons/no_play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                    playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                    deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/no_record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier Prime", 28), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/no_mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier Prime", 28), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        elif(self.state == "recording"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#DADADA", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier Prime", 26), text_color="#BDBDBD", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier Prime", 24), text_color="#BDBDBD")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/no_play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="End Recording", font=("Courier Prime", 28), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.stopRecording())
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#427FF6", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/no_mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier Prime", 28), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        elif(self.state == "disabled"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#DADADA", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier Prime", 26), text_color="#BDBDBD", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier Prime", 24), text_color="#BDBDBD")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/no_play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/no_record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier Prime", 28), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/no_mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier Prime", 28), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        # update window with new graphics
        self.window.update()

    def startRecording(self):
        self.state = "recording"
        self.stateText = "Recording in progress\n"
        self.updateGraphics()
        brain.recordMovement(REFRESH_RATE)
    
    def stopRecording(self):
        armoldGUI.state = "disabled"
        armoldGUI.stateText = "Returning Armold\nto home positions..."
        armoldGUI.updateGraphics()
        brain.robot.goHome()
        time.sleep(1)
        for child in self.window.winfo_children():
            child.destroy()
        self.windowFrame = tk.Frame(self.window).pack()
        recordingframeborder = tk.Frame(self.windowFrame, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        recordingframeborder.pack(side="top", expand=True, fill="both")
        recordingInfoLabelBorder = tk.Frame(recordingframeborder, background="#FFFFFF", height=0.25*self.screenheight)
        recordingInfoLabelBorder.pack(side="top", expand=False, fill="both", padx=self.borderPadding, pady=(0.25*self.screenheight,self.borderPadding))
        self.infoLabel = ctk.CTkLabel(recordingInfoLabelBorder, text="Nice! Your recording is complete...\nWhat did you just teach Armold to do?", font=("Courier Prime", 52), text_color="#000000")
        self.infoLabel.pack(side="top", expand=False, fill="both")
        recordingEntriesBorder = tk.Frame(recordingframeborder, background="#FFFFFF", height=0.1*self.screenheight)
        recordingEntriesBorder.pack(side="top", expand=False, fill="both", padx=5*self.borderPadding, pady=self.borderPadding)
        self.recordingName = tk.StringVar()
        recordingNameEntry = ctk.CTkEntry(recordingEntriesBorder, textvariable=self.recordingName, placeholder_text="", font=("Courier Prime", 32), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", border_color="#5D6D8B", border_width=self.borderPadding, corner_radius=15)
        recordingNameEntry.pack(side="left", expand=True, fill="both")
        self.recordingName.trace_add("write", lambda *args: recordingNameEntry.delete(25))
        cancelImage = ctk.CTkImage(Image.open("gui_icons/cancel.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        cancelButton = ctk.CTkButton(recordingEntriesBorder, image=cancelImage, text="Cancel", font=("Courier Prime", 32), text_color="#842C2C", fg_color="#F64242", bg_color="#FFFFFF", hover_color="#F64242", border_color="#842C2C", border_width=self.borderPadding, corner_radius=15, command=lambda : self.cancelRecording())
        cancelButton.pack(side="right", expand=False, fill="both")
        acceptImage = ctk.CTkImage(Image.open("gui_icons/accept.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        acceptButton = ctk.CTkButton(recordingEntriesBorder, image=acceptImage, text="Accept", font=("Courier Prime", 32), text_color="#34B801", fg_color="#42F65E", bg_color="#FFFFFF", hover_color="#42F65E", border_color="#34B801", border_width=self.borderPadding, corner_radius=15, command=lambda : self.acceptRecording())
        acceptButton.pack(side="right", expand=False, fill="both")
        self.window.update()
        recordingNameEntry.focus_force()
        os.system("dbus-send --type=method_call --print-reply --dest=org.onboard.Onboard /org/onboard/Onboard/Keyboard org.onboard.Onboard.Keyboard.Show")
        while (self.state == "disabled"):
            self.window.update()
    
    def acceptRecording(self):
        name = self.recordingName.get()
        if(len(name) < 1):
            return
        if(not name.isprintable()):
            self.infoLabel.configure(text="Please make sure to only include\nalphanumeric characters in your name!")
            self.infoLabel.update()
            return
        os.system("dbus-send --type=method_call --print-reply --dest=org.onboard.Onboard  /org/onboard/Onboard/Keyboard org.onboard.Onboard.Keyboard.Hide")
        name = name.replace(" ", "_")
        brain.saveRecordedMovement(name, REFRESH_RATE)
        for child in self.window.winfo_children():
            child.destroy()
        testEnv.setupWindow()
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        self.fillWindow()
    
    def cancelRecording(self):
        os.system("dbus-send --type=method_call --print-reply --dest=org.onboard.Onboard  /org/onboard/Onboard/Keyboard org.onboard.Onboard.Keyboard.Hide")
        brain.newMoveTimeline = []
        for child in self.window.winfo_children():
            child.destroy()
        testEnv.setupWindow()
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        self.fillWindow()
    
    def startMirror(self):
        self.state = "mirror"
        self.stateText = "Live control in progress\n"
        self.updateGraphics()
        brain.realtimeMovement(REFRESH_RATE)
    
    def stopMirror(self):
        armoldGUI.state = "disabled"
        armoldGUI.stateText = "Returning Armold\nto home positions..."
        armoldGUI.updateGraphics()
        brain.robot.goHome()
        time.sleep(1)
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        self.updateGraphics()
    
    def startPlayback(self, name):
        self.state = "playback"
        niceName = name.replace("_", " ")
        self.stateText = f"Playing\n{niceName}"
        self.playing = name
        self.updateGraphics()
        brain.playbackMovement(name, REFRESH_RATE)
    
    def stopPlayback(self):
        armoldGUI.state = "disabled"
        armoldGUI.stateText = "Returning Armold\nto home positions..."
        armoldGUI.updateGraphics()
        brain.robot.goHome()
        time.sleep(1)
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        self.playing = "NONE"
        self.updateGraphics()
    
    def deleteRecording(self, name):
        displayName = name.replace("_", " ")
        for child in self.window.winfo_children():
            child.destroy()
        self.windowFrame = tk.Frame(self.window).pack()
        recordingframeborder = tk.Frame(self.windowFrame, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        recordingframeborder.pack(side="top", expand=True, fill="both")
        recordingInfoLabelBorder = tk.Frame(recordingframeborder, background="#FFFFFF")
        recordingInfoLabelBorder.pack(side="top", expand=False, fill="both", padx=self.borderPadding, pady=(0.25*self.screenheight,self.borderPadding))
        infoLabel = ctk.CTkLabel(recordingInfoLabelBorder, text=f"Are you sure that you want to\ndelete the recording\n{displayName}?", font=("Courier Prime", 52), text_color="#000000")
        infoLabel.pack(side="top", expand=False, fill="both")
        recordingEntriesBorder = tk.Frame(recordingframeborder, background="#FFFFFF")
        recordingEntriesBorder.pack(side="top", expand=False, fill="both", padx=5*self.borderPadding, pady=5*self.borderPadding)
        acceptImage = ctk.CTkImage(Image.open("gui_icons/accept.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        acceptButton = ctk.CTkButton(recordingEntriesBorder, image=acceptImage, text="Accept", font=("Courier Prime", 32), text_color="#34B801", fg_color="#42F65E", bg_color="#FFFFFF", hover_color="#42F65E", border_color="#34B801", border_width=self.borderPadding, corner_radius=15, command=lambda : self.acceptDelete(name))
        acceptButton.pack(side="left", expand=True, fill="both", padx=5*self.borderPadding)
        cancelImage = ctk.CTkImage(Image.open("gui_icons/cancel.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        cancelButton = ctk.CTkButton(recordingEntriesBorder, image=cancelImage, text="Cancel", font=("Courier Prime", 32), text_color="#842C2C", fg_color="#F64242", bg_color="#FFFFFF", hover_color="#F64242", border_color="#842C2C", border_width=self.borderPadding, corner_radius=15, command=lambda : self.cancelDelete())
        cancelButton.pack(side="right", expand=True, fill="both", padx=5*self.borderPadding)
        self.window.update()
    
    def acceptDelete(self, name):
        brain.deleteMovement(name)
        for child in self.window.winfo_children():
            child.destroy()
        testEnv.setupWindow()
        self.fillWindow()
    
    def cancelDelete(self):
        for child in self.window.winfo_children():
            child.destroy()
        testEnv.setupWindow()
        self.fillWindow()
    
    def toggleLoop(self):
        self.playbackLoop = not self.playbackLoop
        self.updateGraphics()
        
    def updatePlaybackDuration(self, val):
        self.playbackDuration.configure(text=val)
        self.playbackDuration.update()
    
    def showDebugWindow(self):
        testEnv.showWindow()
    
    def closeWindow(self):
        self.window.destroy()
        sys.exit()
        # TODO uncomment this when all done!
        # os.system("sudo reboot")

class Connection:
    def __init__(connection):
        connection.client = mqtt_helper.MqttClient()
        connection.setup()
        
    def setup(connection):
        connection.client.callback = lambda type, payload: connection.mqtt_callback(type, payload)
        connection.client.connect("Armold/ToDummy", "Armold/ToBrain", use_off_campus_broker=False)
    
    def mqtt_callback(connection, type_name, payload):
        pass

# handles re-establishing wireless connection if it fails
def handleConnectionError():
    armoldGUI.state = "disabled"
    armoldGUI.stateText = "Sorry, Armold is having trouble\nfinding its arm... trying again..."
    armoldGUI.updateGraphics()
    while True:
        try:
            connection.client.client.reinitialise()
            connection.setup()
            break
        except Exception as error:
            time.sleep(1)
    armoldGUI.state = "disabled"
    armoldGUI.stateText = "Arm found! Armold is ready to go!\n"
    armoldGUI.updateGraphics()
    time.sleep(1)
    armoldGUI.state = "disabled"
    armoldGUI.stateText = "Returning Armold\nto home positions..."
    armoldGUI.updateGraphics()
    brain.robot.goHome()
    time.sleep(1)
    armoldGUI.state = "idle"
    armoldGUI.stateText = "Nothing in progress\n"
    armoldGUI.updateGraphics()

# setup system and verify arduino working
try:
    brain = ArmoldBrain()
except Exception as error:
    print("There was an issue initializing Armold...\nAre you sure the control panel's Arduino is plugged in and flashed correctly?\n\nCtrl+C to close and retry...", flush=True)
    sys.stderr = None
    while True:
        pass

# create GUI elements
root = tk.Tk()
testEnv = TestEnvironment()
armoldGUI = ArmoldGUI()
# setup wireless connection
while True:
    try:
        armoldGUI.state = "disabled"
        armoldGUI.stateText = "Armold is awake! \nNow looking for its arm..."
        armoldGUI.updateGraphics()
        connection = Connection()
        brain.robot.goHome()
        time.sleep(1)
        armoldGUI.state = "disabled"
        armoldGUI.stateText = "Arm found!\nArmold is ready to go!"
        armoldGUI.updateGraphics()
        time.sleep(1)
        armoldGUI.state = "idle"
        armoldGUI.stateText = "Nothing in progress\n"
        armoldGUI.updateGraphics()
        break
    except Exception as error:
        armoldGUI.state = "disabled"
        armoldGUI.stateText = "Sorry, Armold is having trouble\nfinding its arm... trying again..."
        armoldGUI.updateGraphics()
        time.sleep(1)
# main loop
while True:
    armoldGUI.window.update()

# extra code for use in case of needing to ZERO out the stepper motor's tracked position
# (otherwise, should always go to "ZERO" at home; so if powered off after at home, can manually adjust gear positioning)
# # zero stepper tracking
# elif(command == "z"):
#     print("\nYou told Armold to zero its stepper motor tracking.")
#     connection.client.send_message("command", "RESET\nRESET")
#     connection.client.client.loop(timeout = 1.0)
#     time.sleep(1)