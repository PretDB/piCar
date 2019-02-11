import multiprocessing as mp
import threading
import time
from command import Command


class FireFunc(mp.Process):    # {{{
# Init {{{
    def __init__(self, m, cchannel, dchannel, com, fire):
        mp.Process.__init__(self)
        self.m = m
        self.control = cchannel
        self.detect = dchannel
        # self.m.pinMode(self.control, 0)
        # self.m.pinMode(self.detect, 1)
        print(bin(self.m.regRead(0x01)))

        self.com = com
        self.fire = fire

        pass
# }}}

    def on(self):
        # self.m.pinMode(self.control, 0)
        self.m.digitalWrite(self.control, 1)
        print(self.m.digitalRead(self.control))
        print('jjjj')
        return

    def off(self):
        # self.m.pinMode(self.control, 0)
        self.m.digitalWrite(self.control, 0)
        return

    # Run, main thread loop {{{
    def run(self):
        while True:
            if bool(self.fire.value):
                print('fire')
                if self.m.digitalRead(self.detect) == 1:
                    print('got fire')
                    self.on()
                    print('on fire')
                    time.sleep(5)
                    continue
                else:
                    # self.m.pinMode(self.control, 0)
                    # self.m.digitalWrite(self.control, 0)
                    pass

            print('off fire')
            # self.m.pinMode(self.control, 0)
            self.m.digitalWrite(self.control, 0)
            time.sleep(0.2)

        pass
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
# }}}
