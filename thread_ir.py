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

        self.m.pinMode(self.llchannel, 1)
        self.m.pinMode(self.hlchannel, 1)
        self.m.pinMode(self.hrchannel, 1)
        self.m.pinMode(self.rrchannel, 1)


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

                if llstate == 0 or hlstate == 0:
                    self.car.move(Command.RightRotate)
                elif hrstate == 0 or rrstate == 0:
                    self.car.move(Command.LeftRotate)
                elif hlstate == 0 and hrstate == 0:
                    self.car.move(Command.RightRotate)
                else:
                    self.car.move(Command.Forward)

            time.sleep(0.1)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
