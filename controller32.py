#!/usr/bin/python3
import wiringpi
import sys
import time
from multiprocessing import Value
from ctypes import c_int, c_float

from command import Command
import server
import carLower
import thread_tracker
import thread_sd
import ridar2


# Server related initialations.
recvCom = Value('I', 0)
recvFire = Value('I', 0)
recvSpeed = Value('f', 0.0)
webServer = server.server(recvCom, recvFire, recvSpeed)
webServer.daemon = True
webServer.start()

# Car class initiations.
car = carLower.CarLower()
ridar = ridar2.RidarFunc(car, recvCom)
sd = thread_sd.SDFunc(False, car, recvCom)
tracker = thread_tracker.tracker(videoDev='/dev/tracker',
                                 car=car,
                                 com=recvCom,
                                 debug=False)

try:
    while True:
        # Check command to see if it is track or sound detect or something else
        # that carLower can not process.
        speed = float(recvSpeed.value)
        com = Command(recvCom.value)
        fire = bool(recvFire.value)

        print(str(com.value), str(speed), str(fire), str(com.value & 0x0F))
        car.setState(com, speed, fire)
        if com == Command.Track:
           tracker.run()
        elif com == Command.Ridar:
           ridar.run()
        elif com == Command.SoundDetect:
            sd.run()
        time.sleep(0.1)
        pass 
finally:
    car.move(Command.Stop)
    ridar.ridar.deinitRidar()
    sys.exit(-1)
