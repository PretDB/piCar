import wiringpi
from ctypes import c_int, c_float

from command import Command


class CarLower():
    def __init__(self):
        self.serialPort = wiringpi.serialOpen('/dev/ttyAMA0', 9600)
        self.speed = 0.75
        self.fire = False
        pass

    # @param command: int
    # @param runSpeed: float
    # @param fireEnabled: bool or int
    def setState(self, command, runSpeed, fireEnabled):
        com = (command.value)
        if com == 100:
            com = 0
        speed = int(runSpeed * 7)
        fire = int(fireEnabled)
        data = ((fire& 0x01) << 7) | ((speed& 0x07) << 4) | ((com& 0x0F) << 0)
        wiringpi.serialPutchar(self.serialPort, data)
        self.speed = runSpeed
        self.fire = fireEnabled
        pass


    def move(self, command):
        self.setState(command, 0.45, self.fire)
        pass
