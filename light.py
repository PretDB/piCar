import threading
import time
import command
import mcp


class LightFunc(threading.Thread):    # {{{
    def __init__(self, m, front, left, right):
        threading.Thread.__init__(self)

        self.m = m
        self.front = front
        self.left = left
        self.right = right

        self.m.pinMode(self.front, 1)
        self.m.pinMode(self.left, 1)
        self.m.pinMode(self.right, 1)

        pass

    def run(self):
        global com
        global idleTime
        global car

        while True:
            if com == command.Command.Light:
                if self.m.digitalRead(self.front) == 0:
                    car.move(command.Command.Forward)
                    print('f')
                    continue

                elif self.m.digitalRead(self.left) == 0:
                    car.move(command.Command.LeftRotate)
                    print('l')
                    continue

                elif self.m.digitalRead(self.right) == 0:
                    car.move(command.Command.RightRotate)
                    print('r')
                    continue

                else:
                    car.move(command.Command.Stop)
                    print('stop')

            time.sleep(idleTime)

        pass
# }}}
