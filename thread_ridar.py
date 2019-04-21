import time
import math
from command import Command
from ctypes import CDLL, c_float, c_int, pointer


class RidarFunc():    # {{{
    # Init {{{
    def __init__(self, car, com):
        self.car = car
        self.com = com
        self.ridar = CDLL('./ridar.so')
        self.ridar.initRidar('/dev/ttyUSB0'.encode('ascii'))
        floatBuff = c_float * 8192
        self.dataCount = c_int(1)
        self.angles = floatBuff()
        self.distances = floatBuff()
        self.anglesp = pointer(self.angles)
        self.distancesp = pointer(self.distances)
        self.ridarBias = 210

        return
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.Sonic or c == Command.IR:
                self.capture()
                self.preprocess()
                cmd = self.postprocess()
                self.car.move(cmd[0])
                time.sleep(cmd[1])
                pass
            else:
                break
        return
    # }}}

    # Data pre-process, fix ridar installation bias.    # {{{
    def preprocess(self):
        for i in range(self.dataCount):
            df2 = self.distances[i] ** 2 + self.ridarBias ** 2\
                - 2 * self.distances[i] * self.ridarBias *\
                math.cos(self.angles[i])
            self.distances[i] = c_float(df2 ** 0.5)
            pass
        return    # }}}

    # Data post-process. Output car move command    # {{{
    def postprocess(self):
        c = (Command.Stop, 0)

        tick = self.dataCount / 360.0
        leftFrontAng = 315.0
        leftMidAng = 270.0
        rightFrontAng = 30.0
        rightMidAng = 5.0
        leftFrontIndex = int(leftFrontAng / tick)
        leftMidIndex = int(leftMidAng / tick)
        rightFrontIndex = int(rightFrontAng / tick)
        rightMidIndex = int(rightMidAng / tick)
        frontDiss = self.distances[rightFrontIndex:]\
            + self.distances[0: leftFrontIndex]
        leftDiss = self.distances[leftFrontIndex: leftMidIndex]
        rightDiss = self.distances[rightMidIndex: rightFrontIndex]

        frontDis = min(frontDiss)
        leftDis = min(leftDiss)
        rightDis = min(rightDiss)

        if rightDis < 500:
            c = (Command.LeftRotate, 0)
        elif leftDis < 500:
            c = (Command.RightRotate, 0)
        elif frontDis < 500:
            c = (Command.RightShift, 2)
        else:
            c = (Command.Forward, 0)
        return c    # }}}

    # Read distance in mm {{{
    def capture(self):
        self.ridar.capture(self.anglesp, self.distancesp, 8192, self.dataCount)
        return
    # }}}

    # Clampp angle.    # {{{
    def _clamp(self, ang):
        if ang < 0.0:
            ang += 360.0
        if ang > 360.0:
            ang -= 360.0

        if ang < 180.0:
            return ang - 90.0
        elif ang < 360:
            return ang - 180.0
        return ang    # }}}
# }}}
