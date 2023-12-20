import os, sys, time, csv, math

valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")
startVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
actualVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
targetVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
mapping = {"shoulderCB":"0","shoulderR":"1","shoulderLR":"2","elbow":"3","wrist":"4","finger1":"5","finger2":"6","finger3":"7","finger4":"8","finger5":"9"}
timeleft = 0.0
frameKey = "init"
smoothingBase = 30
smoothingRate = 1
lastFrame = time.time()
while True:
        try:
            # checking for new target values assigned
            while True:
                with open(fullValPath, "r") as valFile:
                    try:
                        keyLine = valFile.readline()
                        if (keyLine != frameKey):
                            frameKey = keyLine
                            rateLine = valFile.readline()
                            refreshRate = float(rateLine)
                            timeleft = 1.0 / refreshRate
                            if (refreshRate < smoothingBase):
                                smoothingRate = math.floor(smoothingBase / refreshRate)
                            else:
                                smoothingRate = 1
                            reader = csv.reader(valFile)
                            for row in reader:
                                jointName = row[0]
                                jointVal = float(row[1])
                                if jointName in mapping.keys():
                                    jointPin = mapping[jointName]
                                    startVals[jointPin] = targetVals[jointPin]
                                    actualVals[jointPin] = targetVals[jointPin]
                                    targetVals[jointPin] = jointVal
                            lastFrame = time.time() - (timeleft)
                            print("\nNEW FRAME\n")
                        break
                    except Exception:
                        continue
            if (time.time() - lastFrame >= (timeleft / smoothingRate)):
                lastFrame = time.time()
                for pin, actualVal in actualVals.items():
                    startVal = startVals[pin]
                    targetVal = targetVals[pin]
                    deltaVal = targetVal - startVal
                    deltaInterpolated = deltaVal / smoothingRate
                    interpolated = actualVal + deltaInterpolated
                    if (abs(interpolated - targetVal) - abs(deltaInterpolated) <= 0):
                        interpolated = targetVal
                    actualVals[pin] = interpolated
                    # TODO should set the arduino pin to the interpolated value HERE
                print("UPDATE")
            print(actualVals["0"])
            #print(f'{round(actualVals["0"])} target: {round(targetVals["0"])} start {round(startVals["0"])}')
        except Exception:
            raise Exception("Error occurred.")