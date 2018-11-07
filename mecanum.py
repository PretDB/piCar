import motor
from command import Command

class Mecanum:
    def __init__( self, pcaInst, hlP, hrP, tlP, trP, hlC, hrC, tlC, trC):
        self.hl = motor.Motor( pcaInst, hlP, hlC )
        self.hr = motor.Motor( pcaInst, hrP, hrC )
        self.tl = motor.Motor( pcaInst, tlP, tlC )
        self.tr = motor.Motor( pcaInst, trP, trC )

        self.defaultSpeed = 0.3

        return

    def carMove( self, com, speed = self.defaultSpeed ):
        if com == Command.Forward:
            pass
        elif com == Command.Backward:
            pass
        elif com == Command.LeftShift:
            pass
        elif com == Command.RightShift:
            pass
        elif com == Command.LeftRotate:
            pass
        elif com == Command.RightShift:
            pass
        elif com == Command.Stop:
            pass

        return
