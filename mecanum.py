import motor
import time
from command import Command


# Class Mecanum    # {{{
# Port A => HL
# Port B => HR
# Port C => TR
# Port D => TL
class Mecanum:
    def __init__(self, pcaInst, hlP, hrP, tlP, trP,  # {{{
                 mcpInst, hlC, hrC, tlC, trC, enPin):
        self.hl = motor.Motor(pcaInst, hlP, mcpInst, hlC, enPin)
        self.hr = motor.Motor(pcaInst, hrP, mcpInst, hrC, enPin)
        self.tl = motor.Motor(pcaInst, tlP, mcpInst, tlC, enPin)
        self.tr = motor.Motor(pcaInst, trP, mcpInst, trC, enPin)

        self.state = Command.Stop

        self.defaultSpeed = 0.75
        self.shiftGain = 1
        self.rotateGain = 1

        self.enPin = enPin

        return    # }}}

    def move(self, com):    # {{{
        self.carMove(com, self.defaultSpeed)

        # }}}

    def carMove(self, com, speed):    # {{{
        if not com == self.state and not com == Command.Stop:
            self.carMove(Command.Stop, speed)

        if com == Command.Forward:    # {{{
            self.hl.rotate(False, speed*self.shiftGain)
            self.hr.rotate(False, speed*self.shiftGain)
            self.tl.rotate(False, speed)
            self.tr.rotate(False, speed)
            pass    # }}}

        elif com == Command.Backward:    # {{{
            self.hl.rotate(True, speed*self.shiftGain)
            self.hr.rotate(True, speed*self.shiftGain)
            self.tl.rotate(True, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.LeftRotate:    # {{{
            speed = speed * self.rotateGain
            self.hl.rotate(True, speed*self.shiftGain)
            self.hr.rotate(False, speed*self.shiftGain)
            self.tl.rotate(False, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.RightRotate:    # {{{
            speed = speed * self.rotateGain
            self.hl.rotate(False, speed*self.shiftGain)
            self.hr.rotate(True, speed*self.shiftGain)
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
