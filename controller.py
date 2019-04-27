#!/usr/bin/python3
# Imports {{{
# Basic imports {{{
from command import Command
import fake
import server
import sys
import traceback
import time
from multiprocessing import Value
# }}}
# Functional imports {{{
import thread_sonic
import thread_ir
import thread_fire
import thread_tracker
import thread_light
import thread_hd
import thread_sd
# import thread_ridar
import ridar2
# }}}
# }}}


# Global variables {{{
# Environment related {{{
isDebug = False
svr = None
# }}}

# Hardware handles. {{{
pwm = None
pins = None
car = None
# }}}

# Shared variables {{{
recvCom = None
recvFire = None
recvSpeed = None
# }}}

# Task related {{{
irThread = None
lightThread = None
sonicThread = None
fireThread = None
hdThread = None
sdThread = None
trackThread = None
ridarThread = None
# }}}
# }}}


# Main initiations {{{
def initiation():
    global isDebug
    global pwm
    global pins
    global car

    global recvCom
    global recvFire
    global recvSpeed
    global svr

    global fireThread
    global hdThread
    global irThread
    global lightThread
    global sdThread
    global sonicThread
    global trackThread
    global ridarThread

    # if isDebug:
    if False:
        pwm = fake.PCA()
        pins = fake.MCP()
        car = fake.Mecanum()
    else:
        import wiringpi
        import mecanum
        import pca
        import mcp

        pwm = pca.PCA()
        pins = mcp.MCP(channel=0, addr=0)
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(28, wiringpi.OUTPUT)
        wiringpi.digitalWrite(28, wiringpi.HIGH)
        car = mecanum.Mecanum(pwm, 0, 1, 2, 3, pins, 1, 2, 3, 4, 28)
        car.move(Command.Stop)

    # Server related initiation. {{{
    recvCom = Value('I', 0)
    recvFire = Value('I', 0)
    recvSpeed = Value('f', 0.0)

    svr = server.server(recvCom, recvFire, recvSpeed)
    svr.daemon = True
    svr.start()
    # }}}

    # Function related initiations. {{{
    # Only fireThrad works as a thread
    fireThread = thread_fire.FireFunc(pins=pins,
                                      controlPin=13,
                                      detectPin=12,
                                      fire=recvFire)
    fireThread.daemon = True
    fireThread.start()
    hdThread = thread_hd.HDFunc(pins=pins, detectPin=14,
                                car=car, com=recvCom)
    irThread = thread_ir.IRFunc(pins=pins,
                                ll=8, hl=7, hr=6, rr=5,
                                car=car, com=recvCom)
    lightThread = thread_light.LightFunc(pins=pins,
                                         front=10, left=9, right=11,
                                         car=car, com=recvCom)
    sdThread = thread_sd.SDFunc(isDebug, car, recvCom)
    sonicThread = thread_sonic.SonicFunc(pwm=pwm, servoChannel=4, pins=pins,
                                         echo=15, trig=16,
                                         car=car, com=recvCom)
    ridarThread = ridar2.RidarFunc(car=car, com=recvCom)

    trackThread = thread_tracker.tracker(videoDev='/dev/tracker',
                                         car=car, com=recvCom, debug=isDebug)
    # }}}

    sonicThread.servo.setAngle(0)
    time.sleep(1)
    sonicThread.servo.setAngle(180)
    time.sleep(1)
    sonicThread.servo.setAngle(90)
    return
# }}}


# Main process {{{
if __name__ == "__main__":
    isDebug = len(sys.argv) > 1

    initiation()

    # Loop {{{
    try:
        while True:
            com = Command(recvCom.value)
            fire = bool(recvFire.value)
            speed = float(recvSpeed.value)

            # Pass command directly to car
            car.carMove(com, speed)

            if com == Command.HumanDetect:
                hdThread.run()
                pass
            elif com == Command.IR:
                irThread.run()
                pass
            elif com == Command.Light:
                lightThread.run()
                pass
            elif com == Command.Sonic:
                sonicThread.run()
                irThread.run()
                pass
            elif com == Command.SoundDetect:
                sdThread.run()
                pass
            elif com == Command.Track:
                trackThread.run()
            elif com == Command.Ridar:
                ridarThread.run()
                pass
            pass
    # }}}

    # Exception {{{
    except:
        import wiringpi
        car.move(Command.Stop)
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(28, wiringpi.OUTPUT)
        wiringpi.digitalWrite(28, wiringpi.LOW)
        print(traceback.format_exc())
        ridarThread.ridar.deinitRidar()
        sys.exit(-1)
    # }}}
# }}}
