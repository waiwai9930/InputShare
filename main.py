import socket
from multiprocessing import freeze_support

import adbutils
from input.controller import main_loop
from server import server_process_factory
from input.callbacks import callback_context_wrapper
from ui.connecting_window import open_connecting_window

freeze_support()

open_connecting_window()

adb_client = adbutils.AdbClient()
server_process = server_process_factory(adb_client)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 1234))

callbacks = callback_context_wrapper(client_socket, server_process)
main_loop(*callbacks)

print("[Info] Terminated, closing...")
client_socket.close()
server_process.wait()
