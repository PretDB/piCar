import time
from command import Command


class SDFunc():    # {{{
    # Init {{{
    def __init__(self, isDebug, car, com):
        if not isDebug:
            import wiringpi
            self.wiringpi = wiringpi
            self.wiringpi.wiringPiSetup()
            self.wiringpi.pinMode(25, wiringpi.INPUT)

            def trig():
                c = Command(self.com.value)
                if c != Command.SoundDetect:
                    return
                if self.wiringpi is not None:
                    # Disable interrupt
                    self.car.move(Command.RightRotate)
                    time.sleep(3)
                    self.car.move(Command.Stop)
                    # Enable interrupt
                    time.sleep(4.5)
                return

            self.wiringpi.wiringPiISR(25,
                                      self.wiringpi.INT_EDGE_FALLING,
                                      trig)
        else:
            self.wiringpi = None

        self.car = car
        self.com = com

        self.hooked = False
        return
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            time.sleep(0.3)
            c = Command(self.com.value)
            if c != Command.SoundDetect:
                self.car.move(Command.Stop)
                break
        return
    # }}}
# }}}
