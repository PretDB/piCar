import multiprocessing as mp
import time
# import current_cmd
from command import Command


class SonicFunc(mp.Process):    # {{{
    # Init {{{
    def __init__(self, car, com):
        mp.Process.__init__(self)
        self.com = com
        self.car = car

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
                print('sonic running')
            time.sleep(2)
        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
