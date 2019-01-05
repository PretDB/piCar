#!/usr/bin/python3
import sys
import socket
import time
import json
import spidev
import serial
import qmc
import locator
import filter

isDebug = len(sys.argv) > 1

fieldX = 1
fieldY = 1
lastLoc = (0.1, 0.1)

if isDebug:
    import random

    id = 0

else:
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 5000


    # Hardware Initializations
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.3)
    f = filter.Filter(ser)

    fieldX = 6
    fieldY = 4

    id = int(socket.gethostname())

compass = qmc.QMC(True)

# Network Initializations
address = ('<broadcast>', 6868)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS.connect(('8.8.8.8', 80))
localIP = testS.getsockname()[0]
testS.close()
s.bind(('', 9999))
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

loketyr = locator.Locator()
loketyr.start()



heartbeatPackage = {'FromIP': localIP, 'FromID': id, 'FromRole': 'car',
                    'Type': 'heartbeat', 'Msg': None}


heartbeatCount = 0
c = 0


def GetOri():
    global compass

    angle = compass.readAngle()
    return round(angle)


def GetLoc():
    global lastLoc
    global fieldX
    global fieldY
    global loketyr

    leg = False

    x = lastLoc[0]
    y = lastLoc[1]
    t = 0
    if (not isDebug) and f.lokeitid:
        try:
            res = loketyr.loc
            if not res == None:
                tag = res[0]
                if str(id) == tag:
                    xVal = float(res[1])
                    yVal = float(res[2])
                    x = xVal / fieldX
                    y = yVal / fieldY
                    t = tag
            else:
                print('Bad data from LiFi, use last location')
                leg = True
        except ValueError:
            x = lastLoc[0]
            y = lastLoc[1]
    else:
        x = random.random()
        y = random.random()
        # x = round(0.3, 2)
        # y = round(0.3, 2)
    lastLoc = (x, y)
    loc = {'tag': t, 'X': round(1 - lastLoc[0], 2), 'Y': round(lastLoc[1], 2)}
    return (loc, leg)


while True:
    heartbeatCount = heartbeatCount + 1

    # Get location data
    # Debug mode:
    loc = None
    leg = False
    if not isDebug:
        loc, leg = GetLoc()

    ang = GetOri()
    if loc is not None:
        heartbeatPackage['Msg'] = {'position': loc, 'orientation': ang}
    else:
        heartbeatPackage['Msg'] = {'orientation': ang}

    dataRaw = json.dumps(heartbeatPackage)
    dataByte = dataRaw.encode('utf-8')

    s.sendto(dataByte, address)
    print('')
    print(time.ctime(), 'count: ', heartbeatCount, )
    print('Loc: ', loc)

    if not leg:
        time.sleep(0.3)
