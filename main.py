import socket
from multiprocessing import freeze_support

import adbutils
from adb_controller import try_connecting
from input.controller import main_loop
from server import server_process_factory
from input.callbacks import callback_context_wrapper
from ui.connecting_window import open_connecting_window
from utils import is_valid_ipv4_addr, is_valid_ipv6_addr

freeze_support()

open_connecting_window()

adb_client = adbutils.AdbClient()
server_process = server_process_factory(adb_client)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 1234))

callbacks = callback_context_wrapper(adb_client, client_socket, server_process)
main_loop(*callbacks)

print("[Info] Terminated, closing...")
client_socket.close()
server_process.wait()
