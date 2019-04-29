#!/usr/bin/python3
from multiprocessing import Value
import locatorClass
import locatorServer
import getopt
import sys


benchmark = False
release = False
lens = 0
useServo = False
showImg = False

opts, args = getopt.getopt(sys.argv[1:], 'hbl:rsw')
for key, val in opts:
    if key == '-h':
        print('Usage: run [-h] [-b] [-l len] [-r] [-w]')
        print('-h: Show this help.')
        print('-b: Run benchmark, print fps only.')
        print('-l len: Select len, can be 0 or 1.')
        print('-r: Run under release mode, use smaller marker.')
        sys.exit(0)
    if key == '-b':
        benchmark = True
    if key == '-l':
        if val == '0':
            pass
        elif val == '1':
            pass
        else:
            pass
    if key == '-r':
        release = True
    if key == '-s':
        useServo = True
    if key == '-w':
        showImg = True

isDebug = Value('I', 0)
setCalib = Value('I', 0)
server = locatorServer.server(isDebug=isDebug, setCalib=setCalib)
server.daemon = True
server.start()

lctr = locatorClass.Locator(benchmark=benchmark,
                       lens=lens,
                       release=release,
                       useServo=useServo,
                       showImg=showImg,
                       isDebug=isDebug,
                       setCalib=setCalib)
lctr.run()
