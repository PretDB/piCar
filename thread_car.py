import threading
import time
import current_cmd


class carFunc(threading.Thread):
    # Init {{{
    def __init__(self, car):
        threading.Thread.__init__(self)
        self.car = car
        self.running = True
        pass
    # }}}

    # Run, main thread loop {{{
    # This thread send current command to car directly.
    # the car ( mecanum ) will process it correctly.
    def run(self):
        while self.running:
            self.car.carMove(current_cmd.com, current_cmd.args['Speed'])
            time.sleep(0.02)
        pass
    # }}}

    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
