import multiprocessing as mp
import time
from command import Command
import wiringpi


# {{{
class SDFunc(mp.Process):
    # Init {{{
    def __init__(self, car, com):
        mp.Process.__init__(self)

        self.car = car
        self.com = com

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(29, wiringpi.INPUT)

        pass
    # }}}

    def trig(self):
        self.car.move(Command.RightRotate)
        time.sleep(2)
        self.car.move(Command.Stop)
        return

    def untrig():
        return

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.SoundDetect:
                # TODO: This should be confirmed
                wiringpi.wiringPiISR(29, wiringpi.INT_EDGE_FALLING, self.trig)
            else:
                wiringpi.wiringPiISR(29, wiringpi.INT_EDGE_FALLING, self.untrig)
            time.sleep(0.3)
        pass
    # }}}
# }}}
