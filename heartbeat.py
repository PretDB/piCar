#!/usr/bin/python3
import sys
import socket
import time
import json
import spidev
import wiringpi
import serial

isDebug = len(sys.argv) > 1

fieldX = 1
fieldY = 1
lastLoc = (0, 0)

if isDebug:
    import random
else:
    fieldX = 6
    fieldY = 4

# Network Initializations
address = ('<broadcast>', 6868)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS.connect(('8.8.8.8', 80))
localIP = testS.getsockname()[0]
testS.close()
s.bind(('', 9999))
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Hardware Initializations
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000

ser = serial.Serial('/dev/ttyUSB0', 115200)


id = int(socket.gethostname())
heartbeatPackage = {'FromIP':localIP,'FromID':id, 'FromRole':'car','Type':'heartbeat','Msg':None}


heartbeatCount= 0
c = 0

usb = wiringpi.serialOpen('/dev/ttyUSB0', 115200);


def GetLoc():
    global lastLoc
    global fieldX
    global fieldY

    x = 0.0
    y = 0.0
    t = 0
    if not isDebug:
        try:
            # raw = bytes(spi.readbytes(128))
            raw = ser.readline()
            start = raw.rindex(b'^')
            end = raw.rindex(b'$')
            if start < end:
                m = bytes(raw[start : end])
                msg = m.decode(encoding='ascii')
    
                tagIndex = msg.index('T')
                tag = msg[tagIndex + 1]
                if str(id) == str(msg[tagIndex + 1]):
                    xIndex = msg.index('X')
                    yIndex = msg.index('Y')
                    xString = msg[xIndex + 1 : yIndex]
                    yString = msg[yIndex + 1 : ]
                    xVal = float(xString)
                    yVal = float(yString)
                    x = xVal / fieldX
                    y = yVal / fieldY
                    t = tag
                else:
                    print('Error in func GetLoc: tag not right, use last location')
            else:
                print('Error in func GetLoc: message string not valid, use last location')
        except ValueError:
            return None

    else:
        x = round( random.random(), 2)
        y = round( random.random(), 2)
    lastLoc = (x, y)
    loc = {'tag' : t, 'X' : lastLoc[0], 'Y' : lastLoc[1]}
    return loc


while True:
    heartbeatCount= heartbeatCount + 1

    # Get location data
    loc = GetLoc()
    if loc != None:
        heartbeatPackage['Msg'] = {'position' : loc}
    else:
        heartbeatPackage['Msg'] = None

    dataRaw = json.dumps(heartbeatPackage)
    dataByte = dataRaw.encode('utf-8')

    s.sendto(dataByte, address)
    print(time.ctime(), 'count: ', heartbeatCount, )
    print('Data: ', dataByte)
    print('')

    time.sleep(0.2)

