#!/usr/bin/python3
import socket
import time
import json
import spidev


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


id = int(socket.gethostname())
heartbeatPackage = {'FromIP':localIP,'FromID':id, 'FromRole':'car','Type':'heartbeat','Msg':None}


heartbeatCount= 0
c = 0

def GetLoc():
    raw = bytes(spi.readbytes(128))
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
            loc = {'tag' : tag, 'X' : xVal, 'y' : yVal}
            return loc
        else:
            print('tag not right')
            return None
    else:
        print('message string not valid')
        return None

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
    print(heartbeatCount, dataByte)

    time.sleep(0.2)

