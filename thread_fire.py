import threading
import time


class FireFunc(threading.Thread):    # {{{
    # Init {{{
    def __init__(self, pins, controlPin, detectPin, fire):
        threading.Thread.__init__(self)

        self.pins = pins
        self.control = controlPin
        self.detect = detectPin
        self.pins.pinMode(self.control, self.pins.OUTPUT)
        self.pins.pinMode(self.detect, self.pins.INPUT)

        self.fire = fire
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            if bool(self.fire.value):
                if self.pins.digitalRead(self.detect) == self.pins.LOW:
                    self.pins.digitalWrite(self.control, self.pins.LOW)
                    time.sleep(1)
                else:
                    self.pins.digitalWrite(self.control, self.pins.LOW)
            # The fan should be shut down when fire is disabled.
            else:
                self.pins.digitalWrite(self.control, self.pins.LOW)

            time.sleep(0.2)
        pass
    # }}}
# }}}
