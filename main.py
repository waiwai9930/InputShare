import socket
import adbutils

from multiprocessing import freeze_support
from input.controller import main_loop
from server import SERVER_PORT, server_process_factory
from server.receiver import server_receiver_factory
from input.callbacks import callback_context_wrapper
from ui.connecting_window import open_connecting_window
from ui.tray import Notification, tray_thread_factory
from utils import i18n

freeze_support()

open_connecting_window()

adb_client = adbutils.AdbClient()
server_process = server_process_factory(adb_client)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", SERVER_PORT))
receiver_thread = server_receiver_factory(client_socket)
close_tray = tray_thread_factory(client_socket)

callbacks = callback_context_wrapper(client_socket)
main_errno = main_loop(*callbacks)

print("[Info] Terminated, closing...")
client_socket.close()
receiver_thread.join()
server_process.wait()

close_notice = None
match main_errno:
    case None: pass
    case ConnectionAbortedError() | ConnectionResetError():
        close_notice = Notification(
            i18n(["NetworkError", "网络错误"]),
            i18n(["Unexpected connection aborted.", "连接意外中断。"]),
        )
    case _:
        error_name = main_errno.__class__.__name__
        close_notice = Notification(
            i18n(["Error", "错误"]),
            i18n([f"Unknown error: {error_name}", f"未知错误：{error_name}"]),
        )
close_tray(close_notice)
