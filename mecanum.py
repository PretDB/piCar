import motor
import time
from command import Command


# Class Mecanum    # {{{
# Port A => HL
# Port B => HR
# Port C => TR
# Port D => TL
class Mecanum:
    def __init__(self, pcaInst, hlP, hrP, tlP, trP, mcpInst, hlC, hrC, tlC, trC):  # {{{
        self.hl = motor.Motor(pcaInst, hlP, mcpInst, hlC)
        self.hr = motor.Motor(pcaInst, hrP, mcpInst, hrC)
        self.tl = motor.Motor(pcaInst, tlP, mcpInst, tlC)
        self.tr = motor.Motor(pcaInst, trP, mcpInst, trC)

        self.state = Command.Stop

        self.defaultSpeed = 0.2
        self.shiftGain = 1.25

        return    # }}}

    def move(self, com):    # {{{
        self.carMove(com, self.defaultSpeed)

        # }}}

    def carMove(self, com, speed):    # {{{
        if not com == self.state and not com == Command.Stop:
            self.carMove(Command.Stop, speed)
            time.sleep(0.1)

        if com == Command.Forward:    # {{{
            self.hl.rotate(False, speed)
            self.hr.rotate(False, speed)
            self.tl.rotate(False, speed)
            self.tr.rotate(False, speed)
            pass    # }}}

        elif com == Command.Backward:    # {{{
            self.hl.rotate(True, speed)
            self.hr.rotate(True, speed)
            self.tl.rotate(True, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.LeftRotate:    # {{{
            self.hl.rotate(True, speed)
            self.hr.rotate(False, speed)
            self.tl.rotate(False, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.RightRotate:    # {{{
            self.hl.rotate(False, speed)
            self.hr.rotate(True, speed)
            self.tl.rotate(True, speed)
            self.tr.rotate(False, speed)
            pass    # }}}

        elif com == Command.LeftShift:    # {{{
            self.hl.rotate(True, speed*self.shiftGain)
            self.hr.rotate(False, speed*self.shiftGain)
            self.tl.rotate(True, speed)
            self.tr.rotate(False, speed)
            pass    # }}}

        elif com == Command.RightShift:    # {{{
            self.hl.rotate(False, speed*self.shiftGain)
            self.hr.rotate(True, speed*self.shiftGain)
            self.tl.rotate(False, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.Stop:    # {{{
            self.hl.stop()
            self.hr.stop()
            self.tl.stop()
            self.tr.stop()
            pass    # }}}

        self.state = com

        return    # }}}
# }}}
