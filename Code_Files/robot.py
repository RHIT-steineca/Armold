import os, sys, time, csv, math
import pyfirmata

# set intial robot values
startVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
targetVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
# map of joints to arduino pins
pinMapping = {"shoulderCB":0,"shoulderR":1,"shoulderLR":2,"elbow":3,"wrist":4,"finger1":5,"finger2":6,"finger3":7,"finger4":8,"finger5":9}
connections = {}
# acceptable ranges
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":2400,"shoulderLR":270,"elbow":93.3,"wrist":150,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
servoMaxRange = {"shoulderCB":270,"shoulderR":3600,"shoulderLR":270,"elbow":270,"wrist":270,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}

for name, pin in pinMapping.items():
    connections[name] = board.get_pin(f'd:{pin}:s')
    # # 9g micro servos (180°)
    # board.servo_config(pin, 500, 2430, 0)
    # # 20kg medium servos (270°)
    # board.servo_config(pin, 500, 2470, 0)
    # # 25kg medium servos (270°)
    # board.servo_config(pin, 500, 2490, 0)
    # # 40kg medium servos (270°)
    # board.servo_config(pin, 500, 2520, 0)

# initialization
board = pyfirmata.Arduino('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
print("Communication Successfully started")
valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")
frameKey = "init"
frameLen = 0.0
lastFrame = time.time()

def moveArduino():
    for name, pin in pinMapping.items():
        connection = connections[name]
        connection.write(convertAngleToVal(name, actualVals[name]))

def convertAngleToVal(servoName, sensorAngle):
    minVal = arduinoMinVals[servoName]
    maxVal = arduinoMaxVals[servoName]
    minDeg = limitedMinDegs[servoName]
    maxDeg = servoMaxRange[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    calcVal = sensorAngle * valRange / degRange
    return calcVal

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
                            if jointName in mapping.keys():
                                startVals[jointName] = targetVals[jointName]
                                actualVals[jointName] = targetVals[jointName]
                                targetVals[jointName] = jointVal
                        lastFrame = time.time()
                except Exception:
                    continue
            # check for time passed since new frame and interpolate value
            framePercent = (time.time() - lastFrame) / frameLen
            for joint, actualVal in actualVals.items():
                # check to interpolate if within frame duration
                if (framePercent >= 1):
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