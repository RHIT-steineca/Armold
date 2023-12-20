import os, sys, time, csv, math

valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")
startVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
actualVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
targetVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
mapping = {"shoulderCB":"0","shoulderR":"1","shoulderLR":"2","elbow":"3","wrist":"4","finger1":"5","finger2":"6","finger3":"7","finger4":"8","finger5":"9"}
frameKey = "init"
frameLen = 0.0
lastFrame = time.time()
#smoothingBase = 30
#smoothingRate = 1
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
                        #if (refreshRate < smoothingBase):
                        #    smoothingRate = math.floor(smoothingBase / refreshRate)
                        #else:
                        #    smoothingRate = 1
                        reader = csv.reader(valFile)
                        for row in reader:
                            jointName = row[0]
                            jointVal = float(row[1])
                            if jointName in mapping.keys():
                                jointPin = mapping[jointName]
                                startVals[jointPin] = targetVals[jointPin]
                                actualVals[jointPin] = targetVals[jointPin]
                                targetVals[jointPin] = jointVal
                        #lastFrame = time.time() - (timeleft)
                        lastFrame = time.time()
                        print(f"\nNEW FRAME - {keyLine}\n")
                except Exception:
                    continue
            framePercent = (time.time() - lastFrame) / frameLen
            for pin, actualVal in actualVals.items():
                if (framePercent >= 1):
                    interpolated = targetVal
                else:
                    startVal = startVals[pin]
                    targetVal = targetVals[pin]
                    deltaVal = targetVal - startVal
                    deltaInterpolated = deltaVal * framePercent
                    interpolated = startVal + deltaInterpolated
                actualVals[pin] = interpolated
                # TODO should set the arduino pin to the new actual value HERE
            print(f'{framePercent}: {round(startVals["0"])} -> {round(actualVals["0"])} -> {round(targetVals["0"])}')
            
            #if (time.time() - lastFrame >= (timeleft / smoothingRate)):
            #    lastFrame = time.time()
            #    for pin, actualVal in actualVals.items():
            #        startVal = startVals[pin]
            #        targetVal = targetVals[pin]
            #        deltaVal = targetVal - startVal
            #        deltaInterpolated = deltaVal / smoothingRate
            #        interpolated = actualVal + deltaInterpolated
            #        if (abs(interpolated - targetVal) - abs(deltaInterpolated) <= 0):
            #            interpolated = targetVal
            #        actualVals[pin] = interpolated
            #        # TODO should set the arduino pin to the new actual value HERE
            #    print(f'{round(startVals["0"])} -> {round(actualVals["0"])} -> {round(targetVals["0"])}')
        except Exception:
            raise Exception("Error occurred.")