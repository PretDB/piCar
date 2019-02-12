import time
from command import Command


# {{{
class HDFunc():
    # Init{{{
    def __init__(self, pins, detectPin, car, com):
        self.pins = pins
        self.detect = detectPin
        self.car = car
        self.pins.pinMode(self.detect, self.pins.INPUT)

        self.com = com

        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.HumanDetect:
                if self.pins.digitalRead(self.detect) == 1:
                    self.car.move(Command.LeftRotate)
                    time.sleep(3)
                else:
                    self.car.move(Command.Stop)
            else:
                self.car.move(Command.Stop)
                break
        return
    # }}}
# }}}
