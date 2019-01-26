import time
import threading
import current_cmd
from command import Command


class IRFunc(threading.Thread):    # {{{
# Init {{{
    def __init__(self, m, ll, hl, hr, rr, car):
        threading.Thread.__init__(self)
        self.m = m
        self.car = car
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

    def run(self):
        while True:
            if current_cmd.com == Command.IR or current_cmd.com == Command.Sonic:
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
