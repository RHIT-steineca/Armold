import os, sys, time, csv, math
import pyfirmata
from gpiozero import MCP3008

# set intial robot values
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
# map of joints to arduino pins
pinMapping = {"elbow":9}
connections = {}
# acceptable ranges
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":2400,"shoulderLR":270,"elbow":93.3,"wrist":150,"finger1":1,"finger2":1,"finger3":1,"finger4":1,"finger5":1}
servoMaxRange = {"shoulderCB":270,"shoulderR":3600,"shoulderLR":270,"elbow":270,"wrist":270,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"finger1":0,"finger2":0,"finger3":0,"finger4":0,"finger5":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"finger1":180,"finger2":180,"finger3":180,"finger4":180,"finger5":180}

# initialization
board = pyfirmata.Arduino('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
knob = MCP3008(0)

def moveArduino(name):
    pin = pinMapping[name]
    connection = connections[name]
    connection.write(actualVals[name])
    print(f"knob 0: {round(knob.value, 3):1.3f} -- {name}: {convertValToAngle(name, actualVals[name]):3.1f} deg")

def convertValToAngle(servoName, servoValue):
    minVal = arduinoMinVals[servoName]
    maxVal = arduinoMaxVals[servoName]
    minDeg = limitedMinDegs[servoName]
    maxDeg = servoMaxRange[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    percentValue = float((servoValue - minVal) / valRange)
    calcAngle = minDeg + (percentValue * degRange)
    return calcAngle

def convertAngleToVal(servoName, sensorAngle):
    minVal = arduinoMinVals[servoName]
    maxVal = arduinoMaxVals[servoName]
    minDeg = limitedMinDegs[servoName]
    maxDeg = servoMaxRange[servoName]
    valRange = maxVal-minVal
    degRange = maxDeg-minDeg
    calcVal = sensorAngle * valRange / degRange
    return calcVal

for name, val in pinMapping.items():
    if not (name in pinMapping):
        continue
    # directions[name] = arduinoMaxVals[name] - arduinoMinVals[name] / 1
    pin = pinMapping[name]
    connections[name] = board.get_pin(f'd:{pin}:s')
    # # 9g micro servos (180°)
    # board.servo_config(pin, 500, 2430, 0)
    # # 20kg medium servos (270°)
    board.servo_config(pin, 500, 2470, 0)
    # # 25kg medium servos (270°)
    # board.servo_config(pin, 500, 2490, 0)
    # # 40kg medium servos (270°)
    # board.servo_config(pin, 500, 2520, 0)
while(True):
    for name, val in actualVals.items():
        if not (name in pinMapping):
            continue
        actualVals[name] = convertAngleToVal(name, round(knob.value, 3) * limitedMaxDegs[name])
        moveArduino(name)
    time.sleep(1.0/60)
