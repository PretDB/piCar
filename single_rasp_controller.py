#!/usr/bin/python3

import socket
import threading
import wiringpi
import json
import mecanum
import pca
import mcp
import command
import time


com = command.Command.Stop
idleTime = 0.2


class FireFunc(threading.Thread):    # {{{
    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def run(self):
        global com
        global idleTime

        while True:
            time.sleep(idleTime)

        pass
# }}}


class IRFunc(threading.Thread):    # {{{
    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def run(self):
        global com
        global idleTime

        while True:
            time.sleep(idleTime)

        pass
# }}}


class SonicFunc(threading.Thread):    # {{{
    def __init__(self):
        threading.Thread.__init__(self)

        pass

    def run(self):
        global com
        global idleTime
        while True:
            time.sleep(idleTime)

        pass
# }}}


class LightFunc(threading.Thread):    # {{{
    def __init__(self):
        threading.Thread.__init__(self)

        pass

    def run(self):
        global com
        global idleTime

        while True:
            time.sleep(idleTime)

        pass
# }}}


class TrackFunc(threading.Thread):    # {{{
    def __init__(self):
        threading.Thread.__init__(self)

        pass

    def run(self):
        global com
        global idleTime

        while True:
            time.sleep(idleTime)

        pass
# }}}


def GetCommand(jsonString):    # {{{
    global com
    jsonObj = json.loads(jsonString)
    comn = 0

    if jsonObj['Type'] == 'instruction':
        if jsonObj['FromRole'] == 'Controller':
            comn = jsonObj['Command']
            args = jsonObj['Args']

    com = command.Command(comn)

    return com, args    # }}}


if __name__ == "__main__":
    global com
    # Basic hardware initialization
    pwm = pca.PCA()    # Initialization of pca controller
    wiringpi.wiringPiSPISetup(0, 500000)    # SPI Setup
    pins = mcp.MCP(0, 0)    # MCP initialization

    # Car initialization
    car = mecanum.Mecanum(pwm, 1, 2, 3, 4, 1, 2, 3, 4)

    # Prepare network connection
    test = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test.connect(('8.8.8.8', 80))
    localIP = test.getsockname()[0]
    test.close()

    id = int(socket.gethostname())

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 6688

    server.bind((localIP, port))
    server.listen(5)

    mode = 0

    # Other thread initialization    {{{
    trackThread = TrackFunc()
    irThread = IRFunc()
    lightThread = LightFunc()
    sonicThread = SonicFunc()
    fireThread = FireFunc()

    trackThread.start()
    irThread.start()
    lightThread.start()
    sonicThread.start()
    fireThread.start()    # }}}

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
            com, args = GetCommand(data)
            speed = car.defaultSpeed

            if args is not None and args['speed'] is not None:
                speed = args['speed']

            if com.value >= 0 and com.value <= 6:
                car.carMove(com, speed)
