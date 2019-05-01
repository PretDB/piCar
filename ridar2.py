import time
import math
import bisect
import qmc
from command import Command
from ctypes import CDLL, c_float, c_int, pointer


class RidarFunc():    # {{{
    # Init {{{
    def __init__(self, car, com):
        # self.compass = qmc.QMC(False)
        self.car = car
        self.com = com
        self.ridar = CDLL('/home/pi/piCar/ridar.so')
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
            if c == Command.Ridar:
                self.capture()
                self.preprocess()
                cmd = self.postprocess()
                for com, s in cmd:
                    if c == Command.Ridar:
                        self.car.move(com)
                        time.sleep(s)
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
        c = []

        frontLeftAng = 343.0
        frontRightAng = 20.0
        leftFrontAng = 277.0
        leftBackAng = 247.0
        rightFrontAng = 75.0
        rightBackAng = 90.0

        frontLeftIndex = self._firstLessThan(self.angles, frontLeftAng)
        frontRightIndex = self._firstLessThan(self.angles, frontRightAng)
        leftFrontIndex = self._firstLessThan(self.angles, leftFrontAng)
        leftBackIndex = self._firstLessThan(self.angles, leftBackAng)
        rightFrontIndex = self._firstLessThan(self.angles, rightFrontAng)
        rightBackIndex = self._firstLessThan(self.angles, rightBackAng)
        print(frontLeftIndex, frontRightIndex, leftFrontIndex, leftBackIndex, rightBackIndex, rightFrontIndex)

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
            while rightDiss[0] <= 400.0:
                rightDiss.remove(rightDiss[0])
        except:
            return [(Command.Forward, 0)]

        frontLeftDis = min(frontLeftDiss)
        frontRightDis = min(frontRightDiss)
        leftDis = min(leftDiss)
        rightDis = min(rightDiss)
        print(frontLeftDis, frontRightDis, leftDis, rightDis)

        if frontLeftDis < 800.0 or frontRightDis < 800.0 or leftDis < 800.0 or rightDis < 1400.0:
            self.avoidance()
            print('avoidance')
        c.append((Command.Forward, 0))
        return c    # }}}

    # Read distance in mm {{{
    def capture(self):
        self.ridar.capture(self.anglesp, self.distancesp, 8192, self.dataCountp)
        return
    # }}}

    def deinit(self):
        self.ridar.deinitRidar()

    def _firstLessThan(self, lst,value):  
        count = self.dataCount.value
        low, high, mid = 0, count - 1, 0 
        while low <= high:  
            mid = round((low + high) / 2)
            if lst[mid] < value:  
                low = mid + 1  
            elif lst[mid] > value:  
                high = mid - 1
            else:
                return mid  
        return mid

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

    def avoidance(self):
        maxdis = max(self.distances)
        i = list(self.distances).index(maxdis)
        maxdisang = self.angles[i]
        print('maxdis = %f @ %f' % (maxdis, maxdisang))

        # anginit = self.compass.readAngle()
        # targetang = maxdisang + anginit
        # if targetang < 0:
        #     targetang += 360.0
        # while targetang > 360.0:
        #     targetang -= 360.0
        com = None
        targetang = maxdisang
        # diff = abs(targetang - anginit)
        # print('start: %f, target: %f, diff: %f' % (anginit, targetang, diff))
        targetTime = 0
        if targetang > 180: 
            com = Command.LeftRotate
            targetTime = (360 - targetang) * 15.0 / 360
        else:
            com = Command.RightRotate
            targetTime = targetang * 15.0 / 360
        print('Dir: %s, time: %f' % (str(com), targetTime))
        avoidStart = time.time()
        print('Start @: %f' % avoidStart)
        while Command(self.com.value) == Command.Ridar:
            # angc = self.compass.readAngle()
            # print('Ang: %f' % angc)
            # if abs(angc - targetang) > 5.0:
            #     self.car.move(com)
            if time.time() - avoidStart < targetTime:
                self.car.move(com)
                time.sleep(0.1)
            else:
                self.car.move(Command.Stop)
                print('End @: %f' % time.time())
                break
# }}}
