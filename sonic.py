import threading
import time
import servo
import command
import wiringpi


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
