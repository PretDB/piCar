import time
from command import Command


class LightFunc():    # {{{
    # Init {{{
    def __init__(self, pins, front, left, right, car, com):
        self.pins = pins
        self.front = front
        self.left = left
        self.right = right

        self.car = car
        self.com = com

        self.pins.pinMode(self.front, self.pins.INPUT)
        self.pins.pinMode(self.left, self.pins.INPUT)
        self.pins.pinMode(self.right, self.pins.INPUT)

        pass
    # }}}

    # Run, light loop {{{
    def run(self):
        while True:
            time.sleep(0.05)
            c = Command(self.com.value)
            if c == Command.Light:
                if self.pins.digitalRead(self.front) == self.pins.LOW:
                    self.car.move(Command.Forward)
                    continue

                elif self.pins.digitalRead(self.left) == self.pins.LOW:
                    self.car.move(Command.LeftRotate)
                    continue

                elif self.pins.digitalRead(self.right) == self.pins.LOW:
                    self.car.move(Command.RightRotate)
                    continue
                else:
                    self.car.move(Command.Stop)
            else:
                self.car.move(Command.Stop)
                break
        return
    # }}}
# }}}
