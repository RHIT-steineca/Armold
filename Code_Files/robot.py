import os, sys, time, csv, math
import pyfirmata

# set intial robot values
startVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"thumb":0}
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"thumb":0}
targetVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"thumb":0}
smoothingBasis = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"thumb":0}
# map of joints to arduino pins
pinMapping = {"shoulderLR":6,"finger1":12,"finger2":11,"finger3":10,"finger4":9,"thumb":8}
servoTypes = {"shoulderCB":"20kg","shoulderR":"20kg","shoulderLR":"20kg","elbow":"20kg","wrist":"20kg","finger1":"3kg","finger2":"3kg","finger3":"3kg","finger4":"3kg","thumb":"3kg"}
connections = {}
# acceptable ranges
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"thumb":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":2400,"shoulderLR":270,"elbow":93.3,"wrist":150,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"thumb":100}
servoMaxRange = {"shoulderCB":270,"shoulderR":3600,"shoulderLR":270,"elbow":270,"wrist":270,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"thumb":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"thumb":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"thumb":180}

# initialization
board = pyfirmata.ArduinoMega('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
print("Communication Successfully started")
valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")
frameKey = "init"
frameLen = 1.0
lastFrame = time.time()

# map servo connections
for name, pin in pinMapping.items():
    connections[name] = board.get_pin(f'd:{pin}:s')
    servoType = servoTypes[name]
    # 9g micro servos (180°)
    if(servoType == "9g"):
        board.servo_config(pin, 500, 2430, 0)
    # 3kg small servos (180°)
    elif(servoType == "3kg"):
        board.servo_config(pin, 500, 1000, 0)
    # 20kg medium servos (270°)
    elif(servoType == "20kg"):
        board.servo_config(pin, 500, 2470, 0)
    # 25kg medium servos (270°)
    elif(servoType == "25kg"):
        board.servo_config(pin, 500, 2490, 0)
    # 40kg medium servos (270°)
    elif(servoType == "40kg"):
        board.servo_config(pin, 500, 2520, 0)
    # unmapped servos
    else:
        board.servo_config(pin, 500, 2500, 0)

def moveArduino():
    for name, pin in pinMapping.items():
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
                    if (keyLine != frameKey):
                        frameKey = keyLine
                        rateLine = valFile.readline()
                        refreshRate = float(rateLine)
                        frameLen = 1.0 / refreshRate
                        reader = csv.reader(valFile)
                        for row in reader:
                            jointName = row[0]
                            jointVal = float(row[1])
                            if jointName in pinMapping.keys():
                                startVals[jointName] = targetVals[jointName]
                                actualVals[jointName] = targetVals[jointName]
                                if (abs(convertAngleToVal(jointName, jointVal) - convertAngleToVal(jointName, targetVals[joint])) >= smoothingBasis[jointName]):
                                    targetVals[jointName] = jointVal
                        lastFrame = time.time()
                except Exception:
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