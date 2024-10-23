from enum import IntEnum

class ScreenSize:
    width: int
    height: int
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

class ScreenPoint:
    x: int
    y: int
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class ScreenPosition:
    size: ScreenSize
    point: ScreenPoint
    def __init__(self, size: ScreenSize, point: ScreenPoint) -> None:
        self.size = size
        self.point = point

class UserRotation(IntEnum):
    Protrait  = 0
    Landscape = 1
    ProtraitReversed = 2
    LandscapeReversed = 3
