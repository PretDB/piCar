import wiringpi
import pca
import mcp
import command
import servo
import time


class Sonic:
    def __init__(self, pca, channel, mcp, echo, trig):
        self.servo = servo.Servo(pca, channel)
        self.mcp = mcp
        self.trigPin = trig
        self.echoPin = echo

        self.mcp.pinMode(self.trigPin, 0)
        self.mcp.pinMode(self.echoPin, 1)

        pass

    def readCMHere(self):
        self.mcp.digitalWrite(self.trigPin, wiringpi.HIGH)
        time.sleep(0.00001)
        self.mcp.digitalWrite(self.trigPin, wiringpi.LOW)

        while self.mcp.digitalRead(self.echoPin) == 0:
            pass
        startTime = time.time()

        while self.mcp.digitalRead(self.echoPin) == 1:
            pass
        endTime = time.time()

        t = endTime - startTime
        d = t * 343.0 / 2 * 100

        return d

    def setAngle(self, angle):
        self.servo.setAngle(angle)

