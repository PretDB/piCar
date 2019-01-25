import threading
import time
import mcp


class FireFunc(threading.Thread):    # {{{
    def __init__(self, m, cchannel, dchannel):
        threading.Thread.__init__(self)
        self.m = m
        self.control = cchannel
        self.detect = dchannel

        self.m.pinMode(self.control, 0)
        self.m.pinMode(self.detect, 1)

        pass

    def run(self):
        global com
        global fire
        global idleTime

        while True:
            if fire:
                if self.m.digitalRead(self.detect) == 0:
                    self.m.digitalWrite(self.control, 1)
                    time.sleep(5)
                else:
                    self.m.digitalWrite(self.control, 0)

            time.sleep(idleTime)

        pass
# }}}
