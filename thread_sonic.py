import multiprocessing as mp
import time
import servo
import command
from command import Command


class SonicFunc(mp.Process):    # {{{
    # Init {{{
    def __init__(self, pca, channel, mcp, echo, trig, car, com):
        mp.Process.__init__(self)
        try:
            aa = mcp.regs
        except(AttributeError):
            import wiringpi
            print('jj')

        self.servo = servo.Servo(pca, channel)
        self.mcp = mcp
        self.trigPin = trig
        self.echoPin = echo
        self.car = car
        self.com = com

        pass
    # }}}

    # Read distance in cm {{{
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
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.Sonic:
                self.servo.setAngle(135)
                time.sleep(0.5)
                ld = self.readCM()
                self.servo.setAngle(90)
                time.sleep(0.5)
                cd = self.readCM()
                self.servo.setAngle(45)
                time.sleep(0.5)
                rd = self.readCM()

                if cd > 40.0:
                    self.car.move(command.Command.Forward)
                else:
                    if ld > rd:
                        self.car.move(Command.LeftRotate)
                    else:
                        self.car.move(Command.RightRotate)
            time.sleep(2)
        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
