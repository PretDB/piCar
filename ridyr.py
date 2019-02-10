import random
import multiprocessing as mp
import serial


class Ridyr(mp.Process):
    def __init__(self):
        mp.Process.__init__(self)

        self.ser =serial.Serial('/dev/ttyUSB0', 115200, timeout=0.3)
        pass

    def readline(self):
        st = "^B" + str(int(random.random() * 6 + 1)) + "$\n"
        return bytes(st, encoding='ascii')

    def run(self):
        while True:
            code = self.readline()
            print(code)

        return
