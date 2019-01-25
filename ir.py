import mcp
import time
import threading
import command


class IRFunc(threading.Thread):    # {{{
    def __init__(self, m, ll, hl, hr, rr):
        threading.Thread.__init__(self)
        self.m = m
        self.llchannel = ll
        self.hlchannel = hl
        self.hrchannel = hr
        self.rrchannel = rr

        self.m.pinMode(self.llchannel, 1)
        self.m.pinMode(self.hlchannel, 1)
        self.m.pinMode(self.hrchannel, 1)
        self.m.pinMode(self.rrchannel, 1)

        pass

    def run(self):
        global com
        global idleTime
        global car

        while True:
            if com == command.Command.IR:
                llstate = self.m.digitalRead(self.llchannel)
                hlstate = self.m.digitalRead(self.hlchannel)
                hrstate = self.m.digitalRead(self.hrchannel)
                rrstate = self.m.digitalRead(self.rrchannel)

                if llstate == 0 or hlstate == 0:
                    car.move(command.Command.RightRotate)
                elif hrstate == 0 or rrstate == 0:
                    car.move(command.Command.LeftRotate)
                elif hlstate == 0 and hrstate == 0:
                    car.move(command.Command.RightRotate)
                    time.sleep(5)
                else:
                    car.move(command.Command.Forward)

            time.sleep(idleTime)

        pass
# }}}
