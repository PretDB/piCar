import multiprocessing as mp
import time
import command


class carFunc(mp.Process):
    # Init {{{
    def __init__(self, car, com, speed):
        mp.Process.__init__(self)
        self.car = car
        self.running = True
        self.com = com
        self.speed = speed
        pass
    # }}}

    # Run, main thread loop {{{
    # This thread send current command to car directly.
    # the car ( mecanum ) will process it correctly.
    def run(self):
        while self.running:
            try:
                c = command.Command(self.com.value)
                s = self.speed.value
                self.car.carMove(c, s)
            except(BaseException):
                continue
            time.sleep(0.2)
        pass
    # }}}

    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
