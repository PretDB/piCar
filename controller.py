#!/usr/bin/python3
# imports {{{
import thread_sonic
import thread_ir
import thread_fire
import thread_tracker
import thread_light
import thread_car
import fakeCar
import sys
import server
import fake
import traceback
import command
from multiprocessing import Value
# imports}}}


# Attention, all external devices ( fire, ir, light )
# are activated at low level.

# The main program, which initiate the hardware and some threads. {{{
if __name__ == "__main__":
    isDebug = len(sys.argv) > 1
    try:
        isDebug = len(sys.argv) > 1
        # Basic hardware initialization{{{
        if isDebug:
            # Initialization of pca controller
            pwm = fake.PCA()
            pins = fake.MCP()
            car = fake.Mecanum()
        else:
            import wiringpi
            import mecanum
            import pca
            import mcp
            # Initialization of pca controller
            pwm = pca.PCA()
            # pwm.setFreq(8000)
            pins = mcp.MCP(channel=0, addr=0)    # MCP initialization

            # Car wheel initialization
            car = mecanum.Mecanum(pwm, 0, 1, 2, 3, pins, 1, 2, 3, 4)
            car.defaultSpeed = 0.2
            car.move(command.Command.Stop)

            # Wiringpi gpio initialization
            # This is en pin of motor driver.
            wiringpi.wiringPiSetup()
            wiringpi.pinMode(28, wiringpi.OUTPUT)
            wiringpi.digitalWrite(28, wiringpi.HIGH)
        # }}}

        # Process initialization    {{{
        com = Value('I', 0)
        fire = Value('I', 0)
        speed = Value('f', 0.0)

        if isDebug:
            trackThread = thread_tracker.tracker(0, car, com)
            irThread = thread_ir.IRFunc(pins, 8, 7, 6, 5, car, com)
            lightThread = thread_light.LightFunc(pins, 10, 9, 11, car, com)
            sonicThread = thread_sonic.SonicFunc(pwm, 4, pins, 15, 16, car, com)
            fireThread = thread_fire.FireFunc(pins, 13, 12, com, fire)
            carThread = thread_car.carFunc(car, com, speed)
            svr = server.server(com, fire, speed)
        else:
            trackThread = thread_tracker.tracker('/dev/tracker', car, com)
            irThread = thread_ir.IRFunc(pins, 8, 7, 6, 5, car, com)
            lightThread = thread_light.LightFunc(pins, 10, 9, 11, car, com)
            sonicThread = thread_sonic.SonicFunc(pwm, 4, pins, 15, 16, car, com)
            fireThread = thread_fire.FireFunc(pins, 13, 12, com, fire)
            carThread = thread_car.carFunc(car, com, speed)
            svr = server.server(com, fire, speed)

        trackThread.start()
        irThread.start()
        lightThread.start()
        sonicThread.start()
        fireThread.start()
        carThread.start()
        svr.run()
        # }}}

    except(KeyboardInterrupt):
        if not isDebug:
            car.move(command.Command.Stop)
            wiringpi.wiringPiSetup()
            wiringpi.pinMode(28, wiringpi.OUTPUT)
            wiringpi.digitalWrite(28, wiringpi.LOW)
            print('keyboard interrupt')
        print(traceback.format_exc())

        sys.exit(-1)

# End of main func }}}
