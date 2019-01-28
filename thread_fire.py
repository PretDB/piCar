import multiprocessing as mp
import time
from command import Command


class FireFunc(mp.Process):    # {{{
# Init {{{
    def __init__(self, m, cchannel, dchannel, com, fire):
        mp.Process.__init__(self)
        self.m = m
        self.control = cchannel
        self.detect = dchannel

        self.m.pinMode(self.control, 0)
        self.m.pinMode(self.detect, 1)

        self.com = com
        self.fire = fire

        pass
# }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.FireDetect or bool(self.fire.value):
                if self.m.digitalRead(self.detect) == 0:
                    self.m.digitalWrite(self.control, 1)
                    time.sleep(5)
                else:
                    self.m.digitalWrite(self.control, 0)

            self.m.digitalWrite(self.control, 0)
            time.sleep(0.2)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
