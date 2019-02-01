import multiprocessing as mp
import time
from command import Command


# {{{
class SDFunc(mp.Process):
    # Init {{{
    def __init__(self, m, sd, car, com):
        mp.Process.__init__(self)
        self.m = m
        self.sd = sd

        self.car = car
        self.com = com

        self.m.pinMode(self.sd, 1)

        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.HumanDetect:
                # TODO: This should be confirmed
                if self.m.digitalRead(self.hd) == 0:
                    self.car.move(Command.RightRotate)
                    time.sleep(3)
                pass
            time.sleep(0.1)
        pass
    # }}}
# }}}
