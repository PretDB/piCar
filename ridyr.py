import random


class Ridyr:
    def __init__(self):
        pass

    def readline(self):
        st = "^B" + str(int(random.random() * 6 + 1)) + "$\n"
        return bytes(st, encoding='ascii')
