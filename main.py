import socket
from multiprocessing import freeze_support
from input_controller import main_loop
from server import server_process_factory
from callbacks import callback_context_wrapper
from utils import is_valid_ipv4_addr, is_valid_ipv6_addr

adb_addr = input("Please input the wireless debugging address here\n=> ")
if not is_valid_ipv4_addr(adb_addr) and not is_valid_ipv6_addr(adb_addr):
    print("[Error] Invalid wireless debugging address: ", adb_addr)
    exit(1)

if __name__ == "__main__":
    freeze_support()

    server_process = server_process_factory(adb_addr)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 1234))

    [
        keyboard_press_callback,
        keyboard_release_callback,
    ] = callback_context_wrapper(client_socket, server_process)

    main_loop(keyboard_press_callback, keyboard_release_callback)
    print("[Info] Terminated, closing...")
    client_socket.close()
    server_process.wait()
