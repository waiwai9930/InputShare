import re
import locale
import screeninfo

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

def i18n_factory():
    user_language = locale.getdefaultlocale()[0]
    language_index = 0
    if user_language in ["zh", "zh_CN", "zh_HK", "zh_MO", "zh_SG", "zh_TW"]:
        language_index = 1
    def i18n_instance(candidates: list):
        if len(candidates) == 0:
            raise Exception("Empty i18n candidates")
        if language_index < len(candidates):
            return candidates[language_index]
        return candidates[0]
    return i18n_instance
i18n = i18n_factory()

class StopException(Exception):
    """If an event listener callback raises this exception, the current
    listener is stopped.
    """
    pass
