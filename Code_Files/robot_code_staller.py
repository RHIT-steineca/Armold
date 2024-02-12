import secrets

overwriteVals = {"shoulderCB":0,"shoulderR":0,"shoulderLR":0,"elbow":0,"wrist":0,"fingerPTR":0,"fingerMDL":0,"fingerRNG":0,"fingerPKY":0,"fingerTHM":0}

valPath = "//home//pi//"
fullValPath = os.path.join(valPath, "robovals.txt")

while True:
    print("hehehe, overwrote robovals.txt file...")
    with open(fullValPath, "w") as valFile:
        frameKey = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(math.floor(refreshRate) + 5))
        robovalString =  f'{str(frameKey)}\n1'
        for servoname, servoval in overwriteVals.items():
                robovalString += f'\n"{servoname}",{servoval}'