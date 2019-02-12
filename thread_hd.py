import time
from command import Command


# {{{
class HDFunc():
    # Init {{{
    def __init__(self, pins, detectPin, car):
        self.pins = pins
        self.detect = detectPin
        self.car = car

        self.pins.pinMode(self.detect, self.pins.INPUT)

        pass
    # }}}

    # Run, main thread loop {{{
    def detect(self):
        if self.pins.digitalRead(self.detect) == 0:
            self.car.move(Command.RightRotate)
            time.sleep(3)
        pass
    # }}}
# }}}
