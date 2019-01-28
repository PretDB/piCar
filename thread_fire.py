import multiprocessing as mp
import time
# import current_cmd
from command import Command


class FireFunc(mp.Process):    # {{{
# Init {{{
    def __init__(self, com, fire):
        mp.Process.__init__(self)

        self.com = com
        self.fire = fire

        pass
# }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.FireDetect or bool(self.fire.value):
                print('fire running')

            time.sleep(1)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
