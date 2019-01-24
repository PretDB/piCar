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
import servo
import tracker


com = command.Command.Stop
fire = False
idleTime = 0.1


# Attention, all external devices ( fire, ir, light )
# are activated at low level.
class FireFunc(threading.Thread):    # {{{
    def __init__(self, mcp, cchannel, dchannel):
        threading.Thread.__init__(self)
        self.mcp = mcp
        self.control = cchannel
        self.detect = dchannel

        self.mcp.pinMode(self.control, 0)
        self.mcp.pinMode(self.detect, 1)

        pass

    def run(self):
        global com
        global fire
        global idleTime

        while True:
            if fire:
                if self.mcp.digitalRead(self.detect) == 0:
                    self.mcp.digitalWrite(self.control, 1)
                    time.sleep(5)
                else:
                    self.mcp.digitalWrite(self.control, 0)

            time.sleep(idleTime)

        pass
# }}}


class IRFunc(threading.Thread):    # {{{
    def __init__(self, mcp, ll, hl, hr, rr):
        threading.Thread.__init__(self)
        self.mcp = mcp
        self.llchannel = ll
        self.hlchannel = hl
        self.hrchannel = hr
        self.rrchannel = rr

        self.mcp.pinMode(self.llchannel, 1)
        self.mcp.pinMode(self.hlchannel, 1)
        self.mcp.pinMode(self.hrchannel, 1)
        self.mcp.pinMode(self.rrchannel, 1)

        pass

    def run(self):
        global com
        global idleTime
        global car

        while True:
            if com == command.Command.IR:
                llstate = self.mcp.digitalRead(self.llchannel)
                hlstate = self.mcp.digitalRead(self.hlchannel)
                hrstate = self.mcp.digitalRead(self.hrchannel)
                rrstate = self.mcp.digitalRead(self.rrchannel)

                if llstate == 0 or hlstate == 0:
                    car.move(command.Command.RightRotate)
                elif hrstate == 0 or rrstate == 0:
                    car.move(command.Command.LeftRotate)
                elif hlstate == 0 and hrstate == 0:
                    car.move(command.Command.RightRotate)
                    time.sleep(5)
                else:
                    car.move(command.Command.Forward)

            time.sleep(idleTime)

        pass
# }}}


class SonicFunc(threading.Thread):    # {{{
    def __init__(self, pca, channel, mcp, echo, trig):
        threading.Thread.__init__(self)
        self.servo = servo.Servo(pca, channel)
        self.mcp = mcp
        self.trigPin = trig
        self.echoPin = echo

        self.mcp.pinMode(self.trigPin, 0)
        self.mcp.pinMode(self.echoPin, 1)
        self.servo.setAngle(90)

        pass

    def readCM(self):
        self.mcp.digitalWrite(self.trigPin, wiringpi.HIGH)
        time.sleep(0.00001)
        self.mcp.digitalWrite(self. trigPin, wiringpi.LOW)

        while self.mcp.digitalRead(self.echoPin) == 0:
            pass
        startTime = time.time()
        while self.mcp.digitalRead(self.echoPin) == 1:
            pass
        endTime = time.time()

        t = endTime - startTime
        d = t * 343 / 2 * 100

        return d

    def run(self):    # Task loop {{{
        global com
        global idleTime
        global car

        while True:
            if com == command.Command.Sonic:
                self.servo.setAngle(135)
                time.sleep(0.5)
                ld = self.readCM()
                self.servo.setAngle(90)
                time.sleep(0.5)
                cd = self.readCM()
                self.servo.setAngle(45)
                time.sleep(0.5)
                rd = self.readCM()

                if cd > 30 or cd < 10:
                    car.move(command.Command.Forward)
                else:
                    if ld > rd:
                        car.move(command.Command.LeftRotate)
                    else:
                        car.move(command.Command.RightRotate)

                    time.sleep(idleTime * 10)

            time.sleep(idleTime)

        pass    # }}}
# }}}


class LightFunc(threading.Thread):    # {{{
    def __init__(self, mcp, front, left, right):
        threading.Thread.__init__(self)

        self.mcp = mcp
        self.front = front
        self.left = left
        self.right = right

        self.mcp.pinMode(self.front, 1)
        self.mcp.pinMode(self.left, 1)
        self.mcp.pinMode(self.right, 1)

        pass

    def run(self):
        global com
        global idleTime
        global car

        while True:
            if com == command.Command.Light:
                if self.mcp.digitalRead(self.front) == 0:
                    car.move(command.Command.Forward)
                    print('f')
                    continue

                elif self.mcp.digitalRead(self.left) == 0:
                    car.move(command.Command.LeftRotate)
                    print('l')
                    continue

                elif self.mcp.digitalRead(self.right) == 0:
                    car.move(command.Command.RightRotate)
                    print('r')
                    continue

                else:
                    car.move(command.Command.Stop)
                    print('stop')

            time.sleep(idleTime)

        pass
# }}}


class TrackFunc(threading.Thread):    # {{{
    def __init__(self, videoDev):
        threading.Thread.__init__(self)

        self.trakr = tracker.tracker(videoDev)

        pass

    def run(self):
        global com
        global idleTime
        global car

        while True:
            if com == command.Command.Track:
                d = self.trakr.getDir()
                car.move(d)

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


if __name__ == "__main__":    # {{{
    global com
    # Basic hardware initialization
    pwm = pca.PCA()    # Initialization of pca controller
    # pwm.setFreq(8000)
    pins = mcp.MCP(channel=0, addr=0)    # MCP initialization

    # Car initialization
    car = mecanum.Mecanum(pwm, 0, 1, 2, 3, pins, 1, 2, 3, 4)
    car.defaultSpeed = 0.2

    # wiringpi gpio initialization
    # This is en pin of motor driver.
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(28, wiringpi.OUTPUT)
    wiringpi.digitalWrite(28, wiringpi.HIGH)

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

    # Other thread initialization    {{{
    trackThread = TrackFunc('/dev/tracker')
    irThread = IRFunc(pins, 8, 7, 6, 5)
    lightThread = LightFunc(pins, 10, 9, 11)
    sonicThread = SonicFunc(pwm, 4, pins, 15, 16)
    fireThread = FireFunc(pins, 13, 12)

    trackThread.start()
    irThread.start()
    lightThread.start()
    sonicThread.start()
    fireThread.start()    # }}}

    # Main loop    {{{
    try:
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

                if args is not None:
                    # args = json.loads(args)
                    if args.keys().__contains__('Speed'):
                        speed = args['Speed']

                    if args.keys().__contains__('Fire'):
                        fire= args['Fire']
                    pass

                if com.value >= 0 and com.value <= 6:
                    car.carMove(com, speed)
    except BaseException:
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(28, wiringpi.OUTPUT)
        wiringpi.digitalWrite(28, wiringpi.LOW)
    # End of main loop    }}}
# End of main func }}}
