import threading
import time


class FireFunc():    # {{{
# Init {{{
    def __init__(self, pins, controlPin, detectPin):
        threading.Thread.__init__(self)

        self.pins = pins
        self.control = controlPin
        self.detect = detectPin
        self.pins.pinMode(self.control, self.pins.OUTPUT)
        self.pins.pinMode(self.detect, self.pins.INPUT)

        self.detectEnabled = False
# }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            if self.detectEnabled:
                if self.pins.digitalRead(self.detect) == 0:
                    self.pins.digitalWrite(self.control, 1)
                else:
                    self.pins.digitalWrite(self.control, 0)
                    pass

            time.sleep(0.2)
        pass
    # }}}
# }}}
