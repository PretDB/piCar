import time
import servo
from command import Command


class SonicFunc():    # {{{
    # Init {{{
    def __init__(self, pwm, servoChannel, pins, echo, trig, car, com):
        self.servo = servo.Servo(pwm, servoChannel)
        self.pins = pins
        self.trigPin = trig
        self.echoPin = echo
        self.car = car
        self.com = com

        return
    # }}}

    # Read distance in cm {{{
    def readCM(self):
        self.pins.digitalWrite(self.trigPin, 1)
        time.sleep(0.00001)
        self.pins.digitalWrite(self. trigPin, 0)

        while self.pins.digitalRead(self.echoPin) == 0:
            pass
        startTime = time.time()
        while self.pins.digitalRead(self.echoPin) == 1:
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
                self.servo.setAngle(90)
                frontDis = self.readCM()
                if frontDis < 10.0 or frontDis > 40.0:
                    self.car.move(Command.Forward)
                else:
                    self.car.move(Command.Stop)
                    leftAve = 0.0
                    rightAve = 0.0

                    for leftTick in range(3):
                        self.servo.setAngle(leftTick * 30)
                        time.sleep(0.5)
                        leftAve += self.readCM()
                    for rightTick in range(3, 6):
                        self.servo.setAngle(rightTick * 30)
                        time.sleep(0.5)
                        rightAve += self.readCM()

                    leftAve /= 3
                    rightAve /= 3

                    if rightAve > leftAve:
                        self.car.move(Command.RightRotate)
                    else:
                        self.car.move(Command.LeftRotate)
                    time.sleep(2)
                    self.car.move(Command.Stop)
            else:
                self.car.move(Command.Stop)
                break
        return
    # }}}
# }}}
