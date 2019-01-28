import time
import multiprocessing as mp
from command import Command


class IRFunc(mp.Process):    # {{{
    # Init {{{
    def __init__(self, m, ll, hl, hr, rr, car, com):
        mp.Process.__init__(self)
        self.m = m
        self.car = car
        self.com = com

        self.llchannel = ll
        self.hlchannel = hl
        self.hrchannel = hr
        self.rrchannel = rr

        self.com = com


        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.IR or c == Command.Sonic:
                llstate = self.m.digitalRead(self.llchannel)
                hlstate = self.m.digitalRead(self.hlchannel)
                hrstate = self.m.digitalRead(self.hrchannel)
                rrstate = self.m.digitalRead(self.rrchannel)

            time.sleep(1)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
