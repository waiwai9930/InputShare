import re

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

if __name__ == "__main__":
    test_ips = [
        "192.168.1.1:8080",      # Valid
        "10.0.0.1",              # Invalid (no port)
        "255.255.255.255:65535", # Valid
        "256.256.256.256",       # Invalid
        "192.168.1.1:80",        # Valid
        "192.168.1.1.1:70000",   # Invalid
        "192.168.1.1.1:80",      # Valid
    ]
    for ip in test_ips:
        print(f"{ip}: {is_valid_ipv4_addr(ip)}")

    test_ips = [
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334", # Valid
        "::1",                                     # Valid (loopback address)
        "192.168.1.1",                             # Invalid (not a valid IPv6 address)
        "2001:db8::ff00:42:8329",                  # Valid
        "2001:db8:1234:5678:90ab:cdef:ghij:klmn",  # Invalid (invalid hexadecimal digits)
    ]
    for ip in test_ips:
        print(f"{ip}: {is_valid_ipv6_addr(ip)}")