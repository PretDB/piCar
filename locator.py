import socket
import multiprocessing as mp
import time


class Locator(mp.Process):
    def __init__(self):
        # Initialize process
        mp.Process.__init__(self)

        # Initialize network
        self.address = ('<broadcast>', 6875)
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS.connect(('8.8.8.8', 80))
        self.localIP = testS.getsockname()[0]
        testS.close()
        self.skt.bind(('', 6875))

    def run(self):
        while True:
            data, addr = self.skt.recvfrom(1024)
            data = data.decode('utf-8')
            print(data)
            res = self.pattern.search(data)
            if res is not None:
                self.loc = res.groups()
            time.sleep(0.05)
