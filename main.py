import socket
from multiprocessing import freeze_support
from adb_controller import try_connect
from input.controller import main_loop
from server import server_process_factory
from input.callbacks import callback_context_wrapper
from utils import is_valid_ipv4_addr, is_valid_ipv6_addr

# adb_addr = input("Please input the wireless debugging address here\n=> ")
# if not is_valid_ipv4_addr(adb_addr) and not is_valid_ipv6_addr(adb_addr):
#     print("[Error] Invalid wireless debugging address: ", adb_addr)
#     exit(1)
adb_addr = "192.168.119.84:38811"

if __name__ == "__main__":
    freeze_support()

    adb_client = try_connect(adb_addr)
    server_process = server_process_factory(adb_client)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 1234))

    callbacks = callback_context_wrapper(adb_client, client_socket, server_process)
    main_loop(*callbacks)

    print("[Info] Terminated, closing...")
    client_socket.close()
    server_process.wait()
