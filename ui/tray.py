import socket
import threading
import pystray

from typing import Callable
from dataclasses import dataclass
from PIL import Image

from input.controller import schedule_toggle as main_schedule_toggle,\
                             schedule_exit as main_schedule_exit
from scrcpy_client.clipboard_event import SetClipboardEvent
from utils import script_abs_path
from utils.i18n import i18n
from utils.clipboard import Clipboard
from utils.logger import logger, LogType

Menu = pystray.Menu
MenuItem = pystray.MenuItem

tray = None

@dataclass
class Notification:
    title: str
    message: str

def create_tray(client_socket: socket.socket):
    global tray

    def send_clipboard_text():
        nonlocal client_socket
        current_clipboard_content = Clipboard.safe_paste()
        if current_clipboard_content is None:
            return
        event = SetClipboardEvent(current_clipboard_content)
        try:
            client_socket.sendall(event.serialize())
        except Exception as e:
            logger.write(LogType.Error, "Send data error: " + str(e))
            exit_tray()

    def toggle_sync_clipboard(_, item: MenuItem):
        Clipboard.sync_clipboard = not item.checked

    def exit_tray():
        global tray
        main_schedule_exit()
        assert tray is not None
        tray.stop()

    icon_path = script_abs_path(__file__).joinpath("icon.ico")
    tray_img = Image.open(icon_path)
    tray_menu = Menu(
        MenuItem(
            i18n(["Enable sharing", "开启键鼠共享"]),
            main_schedule_toggle),
        Menu.SEPARATOR,
        MenuItem(
            i18n(["Sync clipboard", "同步剪贴板"]),
            action=toggle_sync_clipboard,
            checked=lambda _: Clipboard.sync_clipboard),
        MenuItem(
            i18n(["Send clipboard text", "发送当前剪贴板文本"]),
            send_clipboard_text),
        Menu.SEPARATOR,
        MenuItem(
            i18n(["Exit", "退出"]),
            exit_tray),
    )
    tray = pystray.Icon(
        "InputShare",
        title=i18n(["InputShare", "输入流转"]),
        icon=tray_img,
        menu=tray_menu,
    )
    tray.run()

def tray_thread_factory(client_socket: socket.socket) -> Callable[[Notification | None], None]:
    def close_tray(reason: Notification | None):
        global tray
        assert tray is not None
        if reason is not None:
            tray.notify(reason.message, reason.title)
        tray.stop()

    thread = threading.Thread(target=create_tray, args=[client_socket])
    thread.start()
    return close_tray
