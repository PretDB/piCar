import multiprocessing as mp
import time
# import current_cmd
from command import Command


class LightFunc(mp.Process):    # {{{
    # Init {{{
    def __init__(self, car, com):
        mp.Process.__init__(self)

        self.car = car
        self.com = com

        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.Light:
                print('light running')
            time.sleep(1)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
