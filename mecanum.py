import motor
from command import Command


# Class Mecanum    # {{{
# Port A => HL
# Port B => HR
# Port C => TR
# Port D => TL
class Mecanum:
    def __init__(self, pcaInst, hlP, hrP, tlP, trP, hlC, hrC, tlC, trC):  # {{{
        self.hl = motor.Motor(pcaInst, hlP, hlC)
        self.hr = motor.Motor(pcaInst, hrP, hrC)
        self.tl = motor.Motor(pcaInst, tlP, tlC)
        self.tr = motor.Motor(pcaInst, trP, trC)

        self.defaultSpeed = 0.3

        return    # }}}

    def move(self, com):    # {{{
        self.carMove(com, self.defaultSpeed)

        return    # }}}

    def carMove(self, com, speed):    # {{{
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

        elif com == Command.LeftShift:    # {{{
            self.hl.rotate(True, speed)
            self.hr.rotate(False, speed)
            self.tl.rotate(False, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.RightShift:    # {{{
            self.hl.rotate(False, speed)
            self.hr.rotate(True, speed)
            self.tl.rotate(True, speed)
            self.tr.rotate(False, speed)
            pass    # }}}

        elif com == Command.LeftRotate:    # {{{
            self.hl.rotate(True, speed)
            self.hr.rotate(False, speed)
            self.tl.rotate(True, speed)
            self.tr.rotate(False, speed)
            pass    # }}}

        elif com == Command.RightShift:    # {{{
            self.hl.rotate(False, speed)
            self.hr.rotate(True, speed)
            self.tl.rotate(False, speed)
            self.tr.rotate(True, speed)
            pass    # }}}

        elif com == Command.Stop:    # {{{
            self.hl.stop()
            self.hr.stop()
            self.tl.stop()
            self.tr.stop()
            pass    # }}}

        return    # }}}
# }}}
