import multiprocessing as mp
import time
import current_cmd


class carFunc(mp.Process):
    # Init {{{
    def __init__(self, car):
        mp.Process.__init__(self)
        self.car = car
        self.running = True
        pass
    # }}}

    # Run, main thread loop {{{
    # This thread send current command to car directly.
    # the car ( mecanum ) will process it correctly.
    def run(self):
        while self.running:
            try:
                self.car.carMove(current_cmd.com, current_cmd.args['Speed'])
            except(BaseException):
                continue
            time.sleep(0.5)
        pass
    # }}}

    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
