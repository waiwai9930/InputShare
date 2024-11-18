import time
import screeninfo

from pathlib import Path
from typing import Any, Callable

def clamp(v: int, x: int, y: int) -> int:
    return min(max(v, x), y)

def screen_size() -> tuple[int, int]:
    monitor = screeninfo.get_monitors()[0]
    return monitor.width, monitor.height

def script_abs_path(_file: str) -> Path:
    return Path(_file).resolve().parent

class TimeCounter:
    __count: int = 0
    __timer: float | None = None
    interval_sec: float
    callback: Callable[[int], Any]

    def __init__(self, interval_sec: float, callback: Callable[[int], Any]) -> None:
        self.interval_sec = interval_sec
        self.callback = callback

    def count(self):
        if self.__timer is None:
            self.__count = 1
            self.__timer = time.time()
            return

        self.__count += 1
        current_sec = time.time()
        if current_sec - self.__timer >= self.interval_sec:
            self.callback(self.__count)
            self.__count = 0
            self.__timer = current_sec
