#!/usr/bin/python3

import socket
import time
import threading
import wiringpi
import json


def GetCommand(jsonString):
    jsonObj = json.loads(jsonString)
    if jsonObj['Type'] == 'instruction'and jsonObj['FromRole'] == 'Controller':
        com = jsonObj['Command']
        args = jsonObj['Command']
    return com,args

def SendCommand(com):
    pass

class trackerThread(threading.Thread):
    def __init__(self):
        pass
    
    def run(self):
        pass

if __name__ == "__main__":
    # Prepare network connection
    test = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test.connect(('8.8.8.8', 80))
    localIP = test.getsockname()[0]
    test.close()
    
    id = 1
    tracker = trackerThread()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 6688
    
    server.bind((localIP, port))
    server.listen(5)

    ser = wiringpi.serialOpen('/dev/ttyAMA0', 9600)

    mode = 0

    # Main loop
    while True:
        clientsocket, addr = server.accept()
        print("client connected, address: ", str(addr), flush=True)

        # Get data from this client until no data available
        while True:
            data = clientsocket.recv(1024).decode('utf-8')
            if not data:
                break
            print(data, flush=True)
            com,args = GetCommand(data)

            if not com == 1000:
                wiringpi.serialPutchar(ser, com)

