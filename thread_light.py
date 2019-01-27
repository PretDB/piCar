import multiprocessing as mp
import time
# import current_cmd
from command import Command


class LightFunc(mp.Process):    # {{{
    # Init {{{
    def __init__(self, m, front, left, right, car, com):
        mp.Process.__init__(self)

        self.m = m
        self.front = front
        self.left = left
        self.right = right
        self.car = car

        self.m.pinMode(self.front, 1)
        self.m.pinMode(self.left, 1)
        self.m.pinMode(self.right, 1)

        self.com = com

        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.Light:
                if self.m.digitalRead(self.front) == 0:
                    self.car.move(Command.Forward)
                    continue

                elif self.m.digitalRead(self.left) == 0:
                    self.car.move(Command.LeftRotate)
                    continue

                elif self.m.digitalRead(self.right) == 0:
                    self.car.move(Command.RightRotate)
                    continue

                else:
                    self.car.move(Command.Stop)
            time.sleep(0.1)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
