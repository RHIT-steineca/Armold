import os, sys, time, csv, math
import pyfirmata

# set intial robot values
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
directions = {"shoulderCB":1,"shoulderR":1,"shoulderLR":1,"elbow":1,"wrist":1,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
# map of joints to arduino pins
mapping = {"shoulderCB":6}
connections = {}
# acceptable ranges
minDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
maxDegs = {"shoulderCB":270,"shoulderR":2400,"shoulderLR":270,"elbow":93.3,"wrist":150,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
minServoVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
maxServoVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}
maxServoRange = {"shoulderCB":270,"shoulderR":3600,"shoulderLR":270,"elbow":270,"wrist":270,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}

# TODO should set the arduino pin to the new actual value HERE
# tutorial https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/
# docs https://pypi.org/project/pyFirmata/
def moveArduino(name):
    pin = mapping[name]
    connection = connections[name]
    connection.write(actualVals[name])
    print(f"{name:11s}@ {pin}: {actualVals[name]:1.1f}°")

def convertValToAngle(servoName, servoValue):
    minVal = minServoVals[servoName]
    maxVal = 1
    minDeg = minDegs[servoName]
    maxDeg = maxServoRange[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    percentValue = float((servoValue - minVal) / valRange)
    degValue = minDeg + (percentValue * degRange)
    return degValue
    
# initialization
board = pyfirmata.Arduino('/dev/ttyACM0')
# board = pyfirmata.ArduinoMega('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
for name, val in maxServoRange.items():
    if not (name in mapping):
        continue
    # maxServoVals[name] = maxDegs[name] / maxServoRange[name]
for name, val in directions.items():
    if not (name in mapping):
        continue
    range = maxServoVals[name] - minServoVals[name]
    directions[name] = range / 10
    pin = mapping[name]
    connections[name] = board.get_pin(f'd:{pin}:s')
    # number bigger for better servo!!!!!
    board.servo_config(pin, 0, 20000, 0)
while(True):
    for name, val in actualVals.items():
        if not (name in mapping):
            continue
        actualVals[name] += directions[name]
        if(actualVals[name] < minServoVals[name]):
            actualVals[name] = minServoVals[name]
            directions[name] = directions[name] * -1
        elif(actualVals[name] > maxServoVals[name]):
            actualVals[name] = maxServoVals[name]
            directions[name] = directions[name] * -1
        moveArduino(name)
        time.sleep(.5)