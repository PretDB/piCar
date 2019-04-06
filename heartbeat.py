#!/usr/bin/python3
import sys
import socket
import time
import json
import random

isDebug = len(sys.argv) > 1

name = int(socket.gethostname())


# Network Initializations
address = ('<broadcast>', 6868)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS.connect(('8.8.8.8', 80))
localIP = testS.getsockname()[0]
testS.close()
s.bind(('', 9999))
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


heartbeatPackage = {'FromID': name, 'Type': 'heartbeat', 'Msg': None}


heartbeatCount = 0

while True:
    heartbeatCount = heartbeatCount + 1

    dataRaw = json.dumps(heartbeatPackage)
    dataByte = dataRaw.encode('utf-8')

    s.sendto(dataByte, address)
    print(dataRaw)
    print(time.ctime(), 'count: ', heartbeatCount, )

    time.sleep(0.5)
