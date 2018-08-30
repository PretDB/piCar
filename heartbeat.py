#!/usr/bin/python3
import socket
import time
import json


# address = ('<broadcast>', 6868)
address = ('<broadcast>', 6868)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testS.connect(('8.8.8.8', 80))
localIP = testS.getsockname()[0]
testS.close()
s.bind(('', 9999))
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

id = int(socket.gethostname())
heartbeatPackage = {'FromIP':localIP,'FromID':id, 'FromRole':'car','Type':'heartbeat','Msg':None}
    

dataRaw = json.dumps(heartbeatPackage)
a = 0
while True:
    a = a + 1
    dataByte = dataRaw.encode('utf-8')
    s.sendto(dataByte, address)
    print(a, dataByte)
    time.sleep(5)

