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
from multiprocessing import Value
# imports}}}


# Attention, all external devices ( fire, ir, light )
# are activated at low level.

# The main program, which initiate the hardware and some threads.{{{
if __name__ == "__main__":
    car = fakeCar.Mecanum()
    car.defaultSpeed = 0.2

    # Process initialization    {{{
    com = Value('I', 0)
    fire = Value('I', 0)
    speed = Value('f', 0.0)
    trackThread = thread_tracker.tracker(car, com)
    irThread = thread_ir.IRFunc(car, com)
    lightThread = thread_light.LightFunc(car, com)
    sonicThread = thread_sonic.SonicFunc(car, com)
    fireThread = thread_fire.FireFunc(com, fire)
    carThread = thread_car.carFunc(car, com, speed)
    svr = server.server(com, fire, speed)

    trackThread.start()
    irThread.start()
    lightThread.start()
    sonicThread.start()
    fireThread.start()
    carThread.start()
    svr.run()    # }}}

    # Run server {{{
    # app.run(host='0.0.0.0', port='6688')
    # }}}

    # trackThread.terminate()
    # irThread.terminate()
    # lightThread.terminate()
    # sonicThread.terminate()
    # fireThread.terminate()
    # carThread.terminate()

    trackThread.join()
    irThread.join()
    lightThread.join()
    sonicThread.join()
    fireThread.join()
    carThread.join()

    # except(BaseException):
    #     print('exception')

    #     sys.exit(-1)

# End of main func }}}
