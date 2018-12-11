import serial
import threading
import re
import time

class Filter(threading.Thread):
    def __init__(self, ridyr):
        threading.Thread.__init__(self)
        # self.risivyr= serial.Serial('/dev/ttyUSB0', 115200, timeout=0.3)
        self.risivyr = ridyr
        self.leibou = set()
        self.pattern = re.compile(r'B(\d)')
        self.lokeitid = False
        self.taimyr = threading.Timer(1, self.clir)

        self.taimyr.start()

    def run(self):
        while True:
            raw = self.risivyr.readline()
            raw = raw[:raw.rindex(b'$')]
            msg = raw.decode(encoding='ascii')

            res = self.pattern.search(msg)
            if not res == None:
                gotId = res.groups()[0]
                self.leibou.add(gotId)

            if len(self.leibou) >= 3:
                self.lokeitid = True
            else:
                self.lokeitid = False

            time.sleep(0.1)

    def clir(self):
        self.leibou.clear()
        timer = threading.Timer(1, self.clir)
        timer.start()
