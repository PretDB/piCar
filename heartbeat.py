#!/usr/bin/python3
import sys
import socket
import time
import json
import spidev
import wiringpi
import serial
import qmc

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

    # usb = wiringpi.serialOpen('/dev/ttyUSB0', 115200)

    # Hardware Initializations
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)

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

    x = lastLoc[0]
    y = lastLoc[1]
    t = 0
    if not isDebug:
        try:
            # raw = bytes(spi.readbytes(128))
            raw = ser.readline()
            start = raw.rindex(b'^')
            end = raw.rindex(b'$')
            if start < end:
                m = bytes(raw[start: end])
                msg = m.decode(encoding='ascii')
                print(msg)

                tagIndex = msg.index('T')
                tag = msg[tagIndex + 1]
                if str(id) == str(msg[tagIndex + 1]):
                    xIndex = msg.index('X')
                    yIndex = msg.index('Y')
                    xString = msg[xIndex + 1: yIndex]
                    yString = msg[yIndex + 1:]
                    xVal = float(xString)
                    yVal = float(yString)
                    x = xVal / fieldX
                    y = yVal / fieldY
                    t = tag
                    if x <= 0 or y <= 0 or x > 1 or y > 1:
                        x = lastLoc[0]
                        y = lastLoc[1]
                else:
                    print('Error in func GetLoc: ' +
                          'tag not right, use last location')
            else:
                print('Error in func GetLoc: ' +
                      'message string not valid, use last location')
        except ValueError:
            x = lastLoc[0]
            y = lastLoc[1]
            print('exception')

    else:
        x = round(random.random(), 2)
        y = round(random.random(), 2)
        # x = round(0.3, 2)
        # y = round(0.3, 2)
    lastLoc = (round(x, 2), round(y, 2))
    loc = {'tag': t, 'X': 1 - lastLoc[0], 'Y': lastLoc[1]}
    return loc


while True:
    heartbeatCount = heartbeatCount + 1

    # Get location data
    loc = GetLoc()
    ang = GetOri()
    if loc is not None:
        heartbeatPackage['Msg'] = {'position': loc, 'orientation': ang}
    else:
        heartbeatPackage['Msg'] = {'orientation': ang}

    dataRaw = json.dumps(heartbeatPackage)
    dataByte = dataRaw.encode('utf-8')

    s.sendto(dataByte, address)
    print(time.ctime(), 'count: ', heartbeatCount, )
    print('Data: ', dataByte)
    print('')

    time.sleep(0.2)
