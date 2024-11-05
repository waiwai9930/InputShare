import re
import time
import screeninfo

from pathlib import Path
from typing import Any, Callable

def clamp(v: int, x: int, y: int) -> int:
    return min(max(v, x), y)

def get_ip_from_addr_str(addr: str) -> str:
    match = re.match(r'\[?([a-fA-F0-9:.]+)\]?:\d+$', addr)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid IP address format")

def is_valid_ipv4_addr(ipv4_addr: str) -> bool:
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(:[0-9]{1,5})$'
    return re.match(pattern, ipv4_addr) is not None

def is_valid_ipv6_addr(ip_str):
    # Regular expression for validating an IPv6 address
    perlipv6regex = r'^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|' \
                    r'(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)' \
                    r'(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|' \
                    r'(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|' \
                    r'[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|' \
                    r'(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:' \
                    r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|' \
                    r'(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:' \
                    r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|' \
                    r'(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:' \
                    r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|' \
                    r'(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:' \
                    r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|' \
                    r'(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:' \
                    r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))\s*$'

    # Compile the regex pattern
    ipv6_regex = re.compile(perlipv6regex)

    # Test the input string against the compiled regex pattern
    return bool(ipv6_regex.match(ip_str))

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
