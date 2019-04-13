import time
from command import Command


class IRFunc():    # {{{
    # Init {{{
    def __init__(self, pins, ll, hl, hr, rr, car, com):
        self.car = car
        self.com = com

        self.pins = pins
        self.llchannel = ll
        self.hlchannel = hl
        self.hrchannel = hr
        self.rrchannel = rr
        self.pins.pinMode(self.llchannel, self.pins.INPUT)
        self.pins.pinMode(self.hlchannel, self.pins.INPUT)
        self.pins.pinMode(self.hrchannel, self.pins.INPUT)
        self.pins.pinMode(self.rrchannel, self.pins.INPUT)

        pass
    # }}}

    # Run, ir loop {{{
    def run(self):
        while True:
            time.sleep(0.1)
            c = Command(self.com.value)
            if c == Command.IR or c == Command.Sonic:
                llstate = self.pins.digitalRead(self.llchannel)
                hlstate = self.pins.digitalRead(self.hlchannel)
                hrstate = self.pins.digitalRead(self.hrchannel)
                rrstate = self.pins.digitalRead(self.rrchannel)

                if hlstate == self.pins.LOW and hrstate == self.pins.LOW:
                    self.car.move(Command.RightRotate)
                elif hlstate == self.pins.LOW:
                    self.car.move(Command.RightRotate)
                elif llstate == self.pins.LOW:
                    self.car.move(Command.RightShift)
                elif hrstate == self.pins.LOW:
                    self.car.move(Command.LeftRotate)
                elif rrstate == self.pins.LOW:
                    self.car.move(Command.LeftShift)
                else:
                    self.car.move(Command.Forward)
            else:
                self.car.move(Command.Stop)
                break
        return
    # }}}
# }}}
