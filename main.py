import socket
import sys
import adbutils

from adb_controller import start_adb_server
from multiprocessing import freeze_support
from input.controller import main_loop
from server import ADBConnectionError, InvalidDummyByteException, server_process_factory, try_connect_server
from server.receiver import server_receiver_factory
from input.callbacks import callback_context_wrapper
from ui.connecting_window import open_connecting_window
from ui.tray import tray_thread_factory
from utils.i18n import get_i18n
from utils.logger import LogType, LOGGER
from utils.notification import Notification, send_notification

def close_notification_resolver(errno: Exception | None):
    close_notification = None
    i18n = get_i18n()
    match errno:
        case None: pass
        case ADBConnectionError():
            close_notification = Notification(
                i18n(["ConnectionError", "连接错误"]),
                i18n(["Wired connection failed, please check if the device is connected correctly.", "有线连接失败，请检查是否正确连接设备。"]),
            )
        case socket.timeout | TimeoutError():
            close_notification = Notification(
                i18n(["NetworkError", "网络错误"]),
                i18n(["Connection with device timeout, please retry.", "设备连接超时，请重试。"]),
            )
        case InvalidDummyByteException():
            close_notification = Notification(
                i18n(["NetworkError", "网络错误"]),
                i18n(["Connection with device failed, please retry.", "设备连接失败，请重试。"])
            )
        case ConnectionAbortedError() | ConnectionResetError():
            close_notification = Notification(
                i18n(["NetworkError", "网络错误"]),
                i18n(["Unexpected connection aborted.", "连接意外中断。"]),
            )
        case _:
            error_name = errno.__class__.__name__
            close_notification = Notification(
                i18n(["Error", "错误"]),
                i18n([f"Unknown error: {error_name}", f"未知错误：{error_name}"]),
            )
    adbutils.AdbClient().server_kill()
    LOGGER.write(LogType.Info, "Terminated with: " + str(close_notification))
    send_notification(close_notification)

if __name__ == "__main__":
    freeze_support()

    start_adb_server()
    open_connecting_window()

    server_process = server_process_factory()
    if isinstance(server_process, Exception):
        close_notification_resolver(server_process)
        sys.exit(1)

    client_socket = try_connect_server("localhost")
    if isinstance(client_socket, Exception):
        close_notification_resolver(client_socket)
        sys.exit(1)

    receiver_thread = server_receiver_factory(client_socket)
    close_tray = tray_thread_factory(client_socket)

    callbacks = callback_context_wrapper(client_socket)
    main_errno = main_loop(*callbacks)

    LOGGER.write(LogType.Info, "Terminated, closing...")
    client_socket.close()
    receiver_thread.join()
    server_process.terminate()

    close_notification_resolver(main_errno)
    close_tray()
