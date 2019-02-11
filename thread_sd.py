import multiprocessing as mp
import time
from command import Command
import wiringpi

sdCar = None


def trig():
    global sdCar
    print('sound')
    sdCar.move(Command.RightRotate)
    time.sleep(2)
    sdCar.move(Command.Stop)
    return


def untrig():
    return


# {{{
class SDFunc(mp.Process):
    # Init {{{
    def __init__(self, car, com):
        mp.Process.__init__(self)

        global sdCar

        self.car = car
        self.com = com
        sdCar = self.car

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(29, wiringpi.INPUT)

        pass
    # }}}

    # Run, main thread loop {{{
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.SoundDetect:
                # TODO: This should be confirmed
                wiringpi.wiringPiISR(29, wiringpi.INT_EDGE_FALLING, trig)
                print('set trig')
            else:
                wiringpi.wiringPiISR(29, wiringpi.INT_EDGE_FALLING, untrig)
                print('unset trig')
            time.sleep(0.3)
        pass
    # }}}
# }}}
