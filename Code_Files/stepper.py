import os, sys, time, csv, json, math
import pyfirmata

# set intial robot values
startVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
actualVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
stepperActualVals = {"shoulderR":0}
targetVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":210,"wrist":0,"fingerPTR":180,"fingerMDL":180,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
smoothingBasis = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
# acceptable ranges
limitedMinDegs = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":25,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
limitedMaxDegs = {"shoulderCB":270,"shoulderR":1333,"shoulderLR":270,"elbow":235,"wrist":230,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":100}
actuatorMaxRange = {"shoulderCB":270,"shoulderR":1333,"shoulderLR":270,"elbow":270,"wrist":270,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}
arduinoMinVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}
arduinoMaxVals = {"shoulderCB":180,"shoulderR":180,"shoulderLR":180,"elbow":180, "wrist":180,"fingerPTR":180,"fingerMDL":180,"fingerRNG":180,"fingerPKY":180,"fingerTHM":180}

# initialization
board = pyfirmata.Arduino('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()
print("step code started")
# map actuator connections
stepperConnections = dict()
# stepperConnections["enable"] = board.get_pin(f'd:39:o')
# stepperConnections["enable"].write(1)
# pins that change
stepperConnections["step"] = board.get_pin(f'd:8:o')
stepperConnections["direction"] = board.get_pin(f'd:7:o')
stepperConnections["step"].write(0)
stepperConnections["direction"].write(0)
print("pins set up")

def moveArduino():
    stepperDeltaPos = actualVals["shoulderR"] - stepperActualVals["shoulderR"]
    stepperDirection = -1
    stepperConnections["direction"].write(0)
    if(stepperDeltaPos > 0):
        stepperDirection = 1
        stepperConnections["direction"].write(1)
    for i in range(abs(stepperDeltaPos)):
        time.sleep(0.00001)
        stepperConnections["step"].write(1)
        time.sleep(0.00001)
        stepperConnections["step"].write(0)
        stepperActualVals["shoulderR"] += stepperDirection

# main loop
while True:
    if(actualVals["shoulderR"] == 0):
        print("going to full")
        actualVals["shoulderR"] = 1333
    elif(actualVals["shoulderR"] == 1333):
        print("going to 0")
        actualVals["shoulderR"] = 0
    moveArduino()