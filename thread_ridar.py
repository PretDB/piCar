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
        self.dataCountp = pointer(self.dataCount)
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
        return
        print(self.dataCount.value)
        for i in range(self.dataCount.value):
            df2 = self.distances[i] ** 2 + self.ridarBias ** 2\
                - 2 * self.distances[i] * self.ridarBias *\
                math.cos(self.angles[i])
            self.distances[i] = c_float(df2 ** 0.5)
            pass
        return    # }}}

    # Data post-process. Output car move command    # {{{
    def postprocess(self):
        c = (Command.Stop, 0)

        tick = self.dataCount.value / 360.0
        frontLeftAng = 343.0
        frontRightAng = 20.0
        leftFrontAng = 277.0
        leftBackAng = 247.0
        rightFrontAng = 75.0
        rightBackAng = 90.0

        frontLeftIndex = int(frontLeftAng / tick)
        frontRightIndex = int(frontRightAng / tick)
        leftFrontIndex = int(leftFrontAng / tick)
        leftBackIndex = int(leftBackAng / tick)
        rightFrontIndex = int(rightFrontAng / tick)
        rightBackIndex = int(rightBackAng / tick)

        frontLeftDiss = self.distances[frontLeftIndex: ]
        frontRightDiss = self.distances[: frontRightIndex]
        leftDiss = self.distances[leftBackIndex: leftFrontIndex]
        rightDiss = self.distances[rightFrontIndex: rightBackIndex]

        frontLeftDiss.sort()
        frontRightDiss.sort()
        leftDiss.sort()
        rightDiss.sort()

        try:
            while frontLeftDiss[0] == 0.0:
                frontLeftDiss.remove(0.0)
            while frontRightDiss[0] == 0.0:
                frontRightDiss.remove(0.0)
            while leftDiss[0] == 0.0:
                leftDiss.remove(0.0)
            while rightDiss[0] == 0.0:
                rightDiss.remove(0.0)
        except:
            return (Command.Forward, 0)

        frontLeftDis = min(frontLeftDiss)
        frontRightDis = min(frontRightDiss)
        leftDis = min(leftDiss)
        rightDis = min(rightDiss)
        print(frontLeftDis, frontRightDis, leftDis, rightDis)

        print('logic: %s' % time.time())
        if frontLeftDis < 600.0 and frontRightDis < 600.0:
            c = (Command.RightRotate, 1)
        elif frontLeftDis < 600.0:
            c = (Command.RightRotate, 0)
        elif frontRightDis < 600.0:
            c = (Command.LeftRotate, 0)
        elif leftDis < 600.0:
            c = (Command.RightShift, 0)
        elif rightDis < 1200.0:
            c = (Command.LeftShift, 0)
        else:
            c = (Command.Forward, 0)
        return c    # }}}

    # Read distance in mm {{{
    def capture(self):
        self.ridar.capture(self.anglesp, self.distancesp, 8192, self.dataCountp)
        return
    # }}}

    def deinit(self):
        self.ridar.deinitRidar()

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
