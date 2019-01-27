import multiprocessing as mp
import time
import current_cmd
from command import Command


class FireFunc(mp.Process):    # {{{
# Init {{{
    def __init__(self, m, cchannel, dchannel):
        mp.Process.__init__(self)
        self.m = m
        self.control = cchannel
        self.detect = dchannel

        self.m.pinMode(self.control, 0)
        self.m.pinMode(self.detect, 1)

        pass
# }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            if current_cmd.com == Command.FireDetect:
                if self.m.digitalRead(self.detect) == 0:
                    self.m.digitalWrite(self.control, 1)
                    time.sleep(5)
                else:
                    self.m.digitalWrite(self.control, 0)

            self.m.digitalWrite(self.control, 0)
            time.sleep(0.1)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
