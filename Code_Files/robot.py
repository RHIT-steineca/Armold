import os, sys, time, csv

valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")
startVals = {"0":0, "1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, "9":0}
actualVals = {"0":0, "1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, "9":0}
targetVals = {"0":2500, "1":2500, "2":2500, "3":2500, "4":2500, "5":2500, "6":2500, "7":2500, "8":2500, "9":2500}
mapping = {"shoulderCB":"0","shoulderR":"1","shoulderLR":"2","elbow":"3","wrist":"4","finger1":"5","finger2":"6","finger3":"7","finger4":"8","finger5":"9"}
timeleft = 0.0
smoothingRate = 60
while True:
        try:
            # checking for new target values assigned
            while True:
                with open(fullValPath, "r") as valFile:
                    firstLine = valFile.readline()
                    try:
                        refreshRate = float(firstLine)
                        if (refreshRate > 0):
                            timeleft = 1.0 / refreshRate
                            reader = csv.reader(valFile)
                            for row in reader:
                                jointName = row[0]
                                jointVal = float(row[1])
                                if jointName in mapping.keys():
                                    jointPin = mapping[jointName]
                                    startVals[jointPin] = actualVals[jointPin]
                                    targetVals[jointPin] = jointVal
                            with open(fullValPath, "w") as valFile:
                                valFile.write("-1")
                        break
                    except Exception:
                        continue
            for pin, actualVal in actualVals.items():
                startVal = startVals[pin]
                targetVal = targetVals[pin]
                deltaVal = targetVal - actualVal
                interpolated = startVal + (deltaVal / smoothingRate)
                actualVals[pin] = interpolated
                # TODO should set the arduino pin to the interpolated value HERE
                print(actualVals)
            time.sleep(timeleft / smoothingRate)
        except Exception:
            raise Exception("Error occurred.")