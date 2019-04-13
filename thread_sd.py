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
        else:
            self.wiringpi = None

        self.car = car
        self.com = com

        self.hooked = False
        return
    # }}}

    # Run, main thread loop {{{
    def run(self):
        def trig():
            if self.wiringpi is not None:
                # Disable interrupt
                self.wiringpi.wiringPiISR(25, self.wiringpi.INT_EDGE_FALLING,
                                          untrig)
                self.car.move(Command.RightRotate)
                time.sleep(3)
                self.car.move(Command.Stop)
                # Enable interrupt
                time.sleep(0.5)
                self.wiringpi.wiringPiISR(25, self.wiringpi.INT_EDGE_FALLING,
                                          trig)
            return

        def untrig():
            return

        while True:
            time.sleep(0.3)
            c = Command(self.com.value)
            if c == Command.SoundDetect:
                if (not self.hooked) and (self.wiringpi is not None):
                    self.wiringpi.wiringPiISR(25,
                                              self.wiringpi.INT_EDGE_FALLING,
                                              trig)
                    self.hooked = True
                else:
                    pass
            else:
                if self.wiringpi is not None:
                    self.wiringpi.wiringPiISR(25,
                                              self.wiringpi.INT_EDGE_FALLING,
                                              untrig)
                self.hooked = False
                self.car.move(Command.Stop)
                break
        return
    # }}}
# }}}
