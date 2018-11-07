from enum import Enum, unique


@unique
class Command(Enum):
    Stop = 0
    Forward = 1
    Backward = 2
    LeftShift = 3
    RightShift = 4
    LeftRotate = 5
    RightRotate = 6