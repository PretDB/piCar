from enum import Enum, unique


@unique
class Command(Enum):
    Non = 100
    Stop = 0
    Forward = 1
    Backward = 2
    LeftShift = 3
    RightShift = 4
    LeftRotate = 5
    RightRotate = 6
    IR = 10
    Sonic = 11
    Light = 12
    HumanDetect = 13
    FireDetect = 14
    SoundDetect = 15
    Track = 1000
