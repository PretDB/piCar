import threading
import time
import current_cmd
from command import Command


class LightFunc(threading.Thread):    # {{{
    # Init {{{
    def __init__(self, m, front, left, right, car):
        threading.Thread.__init__(self)

        self.m = m
        self.front = front
        self.left = left
        self.right = right
        self.car = car

        self.m.pinMode(self.front, 1)
        self.m.pinMode(self.left, 1)
        self.m.pinMode(self.right, 1)

        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            if current_cmd.com == Command.Light:
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
# }}}
