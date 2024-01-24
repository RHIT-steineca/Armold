import os, sys, time, csv, math
import pyfirmata

# set intial robot values
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
directions = {"shoulderCB":1,"shoulderR":1,"shoulderLR":1,"elbow":1,"wrist":1,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
# map of joints to arduino pins
pinMapping = {"finger1":6,"elbow":9}
connections = {}
# acceptable ranges
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":2400,"shoulderLR":270,"elbow":93.3,"wrist":150,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
servoMaxRange = {"shoulderCB":270,"shoulderR":3600,"shoulderLR":270,"elbow":270,"wrist":270,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}

def moveArduino(name):
    pin = pinMapping[name]
    connection = connections[name]
    connection.write(actualVals[name])
    print(f"{name:11s}@ {pin}: {convertValToAngle(name, actualVals[name]):1.1f}°")

def convertValToAngle(servoName, servoValue):
    minVal = arduinoMinVals[servoName]
    maxVal = arduinoMaxVals[servoName]
    minDeg = limitedMinDegs[servoName]
    maxDeg = servoMaxRange[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    percentValue = float((servoValue - minVal) / valRange)
    degValue = minDeg + (percentValue * degRange)
    return degValue
    
# initialization
board = pyfirmata.Arduino('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
for name, val in directions.items():
    if not (name in pinMapping):
        continue
    range = arduinoMaxVals[name] - arduinoMinVals[name]
    directions[name] = range / 1
    pin = pinMapping[name]
    connections[name] = board.get_pin(f'd:{pin}:s')
    board.servo_config(pin, 500, 2430, 0)
while(True):
    for name, val in actualVals.items():
        if not (name in pinMapping):
            continue
        actualVals[name] += directions[name]
        if(actualVals[name] < arduinoMinVals[name]):
            actualVals[name] = arduinoMinVals[name]
            directions[name] = directions[name] * -1
        elif(actualVals[name] > arduinoMaxVals[name]):
            actualVals[name] = arduinoMaxVals[name]
            directions[name] = directions[name] * -1
        moveArduino(name)
    time.sleep(1.0/1)