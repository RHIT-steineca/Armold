import os, sys, time, csv, json, math
import pyfirmata

# set intial robot values
startVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
stepperActualVals = {"shoulderR":0}
targetVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":210,"wrist":0,"fingerPTR":180,"fingerMDL":180,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
smoothingBasis = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
# map of joints to arduino pins
pinMapping = dict()
servoTypes = {"shoulderCB":"25kg","shoulderR":"STEP","shoulderLR":"40kg","elbow":"40kg","wrist":"40kg","fingerPTR":"3kg","fingerMDL":"3kg","fingerRNG":"3kg","fingerPKY":"3kg","fingerTHM":"3kg"}
connections = dict()
# acceptable ranges
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":25,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":1333,"shoulderLR":270,"elbow":235,"wrist":230,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":100}
servoMaxRange = {"shoulderCB":270,"shoulderR":1333,"shoulderLR":270,"elbow":270,"wrist":270,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":1333,"shoulderLR":180,"elbow":180, "wrist":180,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}

# initialization
board = pyfirmata.ArduinoMega('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
print("Communication Successfully started")
valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")
fullStepPath = os.path.join(valPath, "stepperPos.txt")
pinsPath = os.path.join(valPath, "Armold//Code_Files//pins.txt")
with open(pinsPath, "r") as pinFile:
    pinFile.readline()
    pinFile.readline()
    pinFile.readline()
    pinMapping = json.loads(pinFile.readline())
frameKey = "init"
frameLen = 1.0
lastFrame = time.time()
time.sleep(1)
try:
    with open(fullStepPath, "r") as stepFile:
        reader = csv.reader(stepFile)
        stepperActualVals = json.loads(stepFile.readline())
except:
    with open(fullStepPath, "w") as stepFile:
        actualValString = str(stepperActualVals).replace("'", '"')
        stepFile.write(f"{actualValString}")

# map servo connections
for name, pin in pinMapping.items():
    servoType = servoTypes[name]
    # Stepper Motor
    if(servoType == "STEP"):
        stepperConnections = dict()
        # pins set high
        stepperConnections["enable"] = board.get_pin(f'd:39:o')
        stepperConnections["sl1"] = board.get_pin(f'd:37:o')
        stepperConnections["sl2"] = board.get_pin(f'd:41:o')
        stepperConnections["enable"].write(0)
        stepperConnections["sl1"].write(0)
        stepperConnections["sl2"].write(0)
        # pins that change
        stepperConnections["step"] = board.get_pin(f'd:43:o')
        stepperConnections["direction"] = board.get_pin(f'd:45:o')
        stepperConnections["step"].write(0)
        stepperConnections["direction"].write(0)
        connections[name] = stepperConnections
    # 9g micro servos (180°)
    elif(servoType == "9g"):
        connections[name] = board.get_pin(f'd:{pin}:s')
        board.servo_config(pin, 500, 2430, 0)
    # 3kg small servos (180°)
    elif(servoType == "3kg"):
        connections[name] = board.get_pin(f'd:{pin}:s')
        board.servo_config(pin, 500, 1000, 0)
    # 20kg medium servos (270°)
    elif(servoType == "20kg"):
        connections[name] = board.get_pin(f'd:{pin}:s')
        board.servo_config(pin, 500, 2470, 0)
    # 25kg medium servos (270°)
    elif(servoType == "25kg"):
        connections[name] = board.get_pin(f'd:{pin}:s')
        board.servo_config(pin, 500, 2490, 0)
    # 40kg medium servos (270°)
    elif(servoType == "40kg"):
        connections[name] = board.get_pin(f'd:{pin}:s')
        board.servo_config(pin, 500, 2520, 0)
    # unmapped servos
    else:
        connections[name] = board.get_pin(f'd:{pin}:s')
        board.servo_config(pin, 500, 2500, 0)

def moveArduino():
    for name, pin in pinMapping.items():
        newVal = round(actualVals[name])
        if(servoTypes[name] == "STEP"):
            stepperConnections = connections[name]
            stepperDeltaPos = actualVals[name] - stepperActualVals[name]
            stepperDirection = -1
            stepperConnections["direction"].write(0)
            if(stepperDeltaPos > 0):
                stepperDirection = 1
                stepperConnections["direction"].write(1)
            for i in range(math.floor(abs(stepperDeltaPos))):
                stepperConnections["enable"].write(1)
                stepperConnections["step"].write(1)
                stepperConnections["enable"].write(0)
                stepperActualVals[name] += stepperDirection
                stepperConnections["enable"].write(1)
                stepperConnections["step"].write(0)
                stepperConnections["enable"].write(0)
                with open(fullStepPath, "w") as stepFile:
                    actualValString = str(stepperActualVals).replace("'", '"')
                    stepFile.write(f"{actualValString}")
        else: 
            connection = connections[name]
            newVal = convertAngleToVal(name, actualVals[name])
            connection.write(newVal)
        print(f"{name:10s}: {newVal}")

def convertAngleToVal(servoName, sensorAngle):
    minVal = arduinoMinVals[servoName]
    maxVal = arduinoMaxVals[servoName]
    minDeg = limitedMinDegs[servoName]
    maxDeg = servoMaxRange[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    calcVal = sensorAngle * valRange / degRange
    return round(calcVal)

# main loop
while True:
    try:
        # checking for new target values assigned
        with open(fullValPath, "r") as valFile:
            try:
                keyLine = valFile.readline()
                rateLine = valFile.readline()
                if("RESET" in str(rateLine)):
                    for name, val in stepperActualVals.items():
                        stepperActualVals[name] = 0
                    with open(fullStepPath, "w") as stepFile:
                        actualValString = str(stepperActualVals).replace("'", '"')
                        stepFile.write(f"{actualValString}")
                    raise Exception("RESET")
                if (keyLine != frameKey and keyLine != ""):
                    frameKey = keyLine
                    refreshRate = float(rateLine)
                    frameLen = 1.0 / refreshRate
                    reader = csv.reader(valFile)
                    for row in reader:
                        jointName = row[0]
                        jointVal = float(row[1])
                        if jointName in pinMapping.keys():
                            startVals[jointName] = targetVals[jointName]
                            actualVals[jointName] = targetVals[jointName]
                            if (abs(jointVal - targetVals[jointName]) >= smoothingBasis[jointName]):
                                targetVals[jointName] = jointVal
                    lastFrame = time.time()
            except Exception as error:
                print(error)
                continue
        # check for time passed since new frame and interpolate value
        framePercent = (time.time() - lastFrame) / frameLen
        for joint, actualVal in actualVals.items():
            # check to interpolate if within frame duration
            if (framePercent >= 1 or actualVals[joint] == targetVals[joint]):
                interpolated = targetVals[joint]
            else:
                startVal = startVals[joint]
                targetVal = targetVals[joint]
                deltaVal = targetVal - startVal
                deltaInterpolated = deltaVal * framePercent
                interpolated = startVal + deltaInterpolated
            # ensure value is within acceptable range
            if(interpolated < limitedMinDegs[joint]):
                interpolated = limitedMinDegs[joint]
            elif(interpolated > limitedMaxDegs[joint]):
                interpolated = limitedMaxDegs[joint]
            actualVals[joint] = interpolated
        moveArduino()
    except Exception:
        raise Exception("Error occurred.")