import os, sys, time, csv, math
import pyfirmata

# set intial robot values
startVals = {"shoulderCB":2500,"shoulderR":2500,"shoulderLR":2500,"elbow":2500,"wrist":2500,"finger1":2500,"finger2":2500,"finger3":2500,"finger4":2500,"finger5":2500}
actualVals = {"shoulderCB":2500,"shoulderR":2500,"shoulderLR":2500,"elbow":2500,"wrist":2500,"finger1":2500,"finger2":2500,"finger3":2500,"finger4":2500,"finger5":2500}
targetVals = {"shoulderCB":2500,"shoulderR":2500,"shoulderLR":2500,"elbow":2500,"wrist":2500,"finger1":2500,"finger2":2500,"finger3":2500,"finger4":2500,"finger5":2500}
# map of joints to arduino pins
mapping = {"shoulderCB":0,"shoulderR":1,"shoulderLR":2,"elbow":3,"wrist":4,"finger1":5,"finger2":6,"finger3":7,"finger4":8,"finger5":9}
# acceptable ranges
minServoVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
maxServoVals = {"shoulderCB":2500,"shoulderR":2500,"shoulderLR":2500,"elbow":2500,"wrist":2500,"finger1":2500,"finger2":2500,"finger3":2500,"finger4":2500,"finger5":2500}

# TODO should set the arduino pin to the new actual value HERE
# tutorial https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/
# docs https://pypi.org/project/pyFirmata/
def moveArduino():
    #for name, val in actualVals.items():
    #    pin = mapping[name]
    #    connection = board.get_pin('a:{pin}:p')
    #    connection.write(val)
    pass

# initialization
board = pyfirmata.Arduino('/dev/ttyACM0')
# board = pyfirmata.ArduinoMega('/dev/ttyACM0')
print("Communication Successfully started")
valPath = "//home//ArmoldSecondary//"
fullValPath = os.path.join(valPath, "robovals.txt")
frameKey = "init"
frameLen = 0.0
lastFrame = time.time()
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
                        # Console log for testing
                        print(f"\n\nNEW FRAME - {keyLine}")
                        print(f'{round(framePercent*100)}% time: {round(startVals["shoulderCB"])} -> {round(actualVals["shoulderCB"])} -> {round(targetVals["shoulderCB"])}')
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
                if(interpolated < minServoVals[joint]):
                    interpolated = minServoVals[joint]
                elif(interpolated > maxServoVals[joint]):
                    interpolated = maxServoVals[joint]
                actualVals[joint] = interpolated
            moveArduino()
            # Console log for testing
            # print(f'{round(framePercent*100)}% time: {round(startVals["shoulderCB"])} -> {round(actualVals["shoulderCB"])} -> {round(targetVals["shoulderCB"])}')
        except Exception:
            raise Exception("Error occurred.")