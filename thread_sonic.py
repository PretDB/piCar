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
        self.pins.pinMode(self.trigPin, self.pins.OUTPUT)
        self.pins.pinMode(self.echoPin, self.pins.INPUT)
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
        c = Command(self.com.value)
        if c == Command.Sonic:
            ang = self.servo.angle
            self.servo.setAngle(90)
            time.sleep(abs(ang - 90) * 0.008)
            frontDis = self.readCM()
            if frontDis < 10.0 or frontDis > 40.0:
                self.car.move(Command.Forward)
            else:
                self.car.move(Command.Stop)
                time.sleep(2)
                leftAve = 0.0
                rightAve = 0.0

                for leftTick in range(3):
                    ang = self.servo.angle
                    self.servo.setAngle(leftTick * 30)
                    time.sleep(abs(leftTick * 30 - ang) * 0.008)
                    leftAve += self.readCM()
                for rightTick in range(3, 6):
                    ang = self.servo.angle
                    self.servo.setAngle(rightTick * 30)
                    time.sleep(abs(rightTick * 30 - ang) * 0.008)
                    rightAve += self.readCM()

                leftAve /= 3
                rightAve /= 3

                if rightAve < leftAve:
                    self.car.move(Command.RightRotate)
                else:
                    self.car.move(Command.LeftRotate)
                time.sleep(2)
                self.car.move(Command.Stop)
        else:
            self.car.move(Command.Stop)
        return
    # }}}
# }}}
