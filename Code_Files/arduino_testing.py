import os, sys, time, csv, math
import pyfirmata

# set intial robot values
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
directions = {"shoulderCB":4.5,"shoulderR":18,"shoulderLR":9,"elbow":15,"wrist":18,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
# map of joints to arduino pins
mapping = {"shoulderCB":0,"shoulderR":1,"shoulderLR":2,"elbow":3,"wrist":4,"finger1":5,"finger2":6,"finger3":7,"finger4":8,"finger5":9}
# acceptable ranges
minDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
maxDegs = {"shoulderCB":45,"shoulderR":180,"shoulderLR":90,"elbow":150,"wrist":180,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
minServoVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
maxServoVals = {"shoulderCB":45,"shoulderR":180,"shoulderLR":90,"elbow":150,"wrist":180,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}

# TODO should set the arduino pin to the new actual value HERE
# tutorial https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/
# docs https://pypi.org/project/pyFirmata/
def moveArduino(name):
    pin = mapping[name]
    #connection = board.get_pin('a:{pin}:p')
    #connection.write(actualVals[name])
    print(f"{name:11s}@ {pin}: {actualVals[name]:5.1f} = {round(convertValToAngle(name, actualVals[name]),1)}°")

def convertValToAngle(servoName, servoValue):
    minVal = minServoVals[servoName]
    maxVal = maxServoVals[servoName]
    minDeg = minDegs[servoName]
    maxDeg = maxDegs[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    percentValue = round(float((servoValue - minVal) / valRange), 1)
    degValue = minDeg + (percentValue * degRange)
    return degValue
    
# initialization
# board = pyfirmata.Arduino('/dev/ttyACM0')
# board = pyfirmata.ArduinoMega('/dev/ttyACM0')
while(True):
    for name, val in actualVals.items():
        actualVals[name] += directions[name]
        if(actualVals[name] < minServoVals[name]):
            actualVals[name] = minServoVals[name]
            directions[name] = directions[name] * -1
        elif(actualVals[name] > maxServoVals[name]):
            actualVals[name] = maxServoVals[name]
            directions[name] = directions[name] * -1
        moveArduino(name)
        time.sleep(0.1)