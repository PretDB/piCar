import socket
import threading
import time
import re


class Locator(threading.Thread):
    def __init__(self):
        # Initialize thread
        threading.Thread.__init__(self)

        # Initialize network
        self.address = ('<broadcast>', 6875);
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS.connect(('8.8.8.8', 80))
        self.localIP = testS.getsockname()[0]
        testS.close()
        self.skt.bind(('', 6875))

        self.pattern = re.compile(r'\^T([0-1])X(\d\.\d+)Y(\d.\d+)\$')
        self.loc = ('0', '0.0', '0.0')


    def run(self):
        while True:
            data, addr = self.skt.recvfrom(1024)
            data = data.decode('utf-8')
            print(data)
            res = self.pattern.search(data)
            if not res == None:
                self.loc = res.groups()
                print(self.loc)
            time.sleep(0.05)
