#!/usr/bin/python3
# imports {{{
import wiringpi
import mecanum
import pca
import mcp
import thread_sonic
import thread_ir
import thread_fire
import thread_tracker
import thread_light
import thread_car
import sys
import server
from multiprocessing import Value
# imports}}}


# Attention, all external devices ( fire, ir, light )
# are activated at low level.

# The main program, which initiate the hardware and some threads.{{{
if __name__ == "__main__":
    try:
        # Basic hardware initialization{{{
        pwm = pca.PCA()    # Initialization of pca controller
        # pwm.setFreq(8000)
        pins = mcp.MCP(channel=0, addr=0)    # MCP initialization

        # Car wheel initialization
        car = mecanum.Mecanum(pwm, 0, 1, 2, 3, pins, 1, 2, 3, 4)
        car.defaultSpeed = 0.2

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
        svr.start()    # }}}

        # Run server {{{
        # app.run(host='0.0.0.0', port='6688')
        # }}}

        # trackThread.terminate()
        # irThread.terminate()
        # lightThread.terminate()
        # sonicThread.terminate()
        # fireThread.terminate()
        # carThread.terminate()

        # trackThread.join()
        # irThread.join()
        # lightThread.join()
        # sonicThread.join()
        # fireThread.join()
        # carThread.join()

    except(BaseException):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(28, wiringpi.OUTPUT)
        wiringpi.digitalWrite(28, wiringpi.LOW)

        sys.exit(-1)

# End of main func }}}
