import socket

def check_tcp_port_usable(port: int, host="127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except OSError:
            return False
        return True

def find_available_port(start_port: int, host="127.0.0.1"):
    port = start_port
    while not check_tcp_port_usable(port, host=host):
        port += 1
    return port
