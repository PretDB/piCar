# !/usr/bin/python3
# Imports {{{
# Basic imports {{{
from command import Command
import fake
import server
import sys
import traceback
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

    if isDebug:
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
        car = mecanum.Mecanum(pwm, 0, 1, 2, 3, pins, 1, 2, 3, 4)
        car.defaultSpeed = 0.2
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
    fireThread = thread_fire.FireFunc(pins=pins, controlPin=13, detectPin=12)
    fireThread.daemon = True
    fireThread.start()
    hdThread = thread_hd.HDFunc(pins=pins, detectPin=14, car=car)
    irThread = thread_ir.IRFunc(pins, 8, 7, 6, 5, car, com)
    lightThread = thread_light.LightFunc(pins, 10, 9, 11, car, com)
    sdThread = thread_sd.SDFunc(car, com)
    sonicThread = thread_sonic.SonicFunc(pwm, 4, pins, 15, 16, car, com)

    if isDebug:
        trackThread = thread_tracker.tracker(0, car, com)
    else:
        trackThread = thread_tracker.tracker('/dev/tracker', car, com)
    # }}}

    pass
# }}}


# Main process
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

            if com == Command.FireDetect:
                pass
            elif com == Command.HumanDetect:
                pass
            elif com == Command.IR:
                pass
            elif com == Command.Light:
                pass
            elif com == Command.Sonic:
                pass
            elif com == Command.SoundDetect:
                pass
            elif com == Command.Track:
                pass
            pass

# Exception {{{
    except(KeyboardInterrupt):
        if isDebug:
            pass
        else:
            import wiringpi
            car.move(Command.Stop)
            wiringpi.wiringPiSetup()
            wiringpi.pinMode(28, wiringpi.OUTPUT)
            wiringpi.digitalWrite(28, wiringpi.LOW)
            print('keyboard interrupt')

        print(traceback.format_exc())
        sys.exit(-1)
# }}}
# }}}
